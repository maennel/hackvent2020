import subprocess
import dataclasses
import pathlib
import sys

import yaml


ROOTDIR = pathlib.Path(__file__).parent


@dataclasses.dataclass
class Result:

    stdout: str = ''
    stderr: str = ''
    exitcode: int = 0


def _find_executable(name):
    exe_paths = [
        pathlib.Path(sys.executable).parent,  # virtualenv
        ROOTDIR / 'bin',  # standalone
        ROOTDIR / 'node_modules' / name / 'bin',
        ROOTDIR / 'node_modules' / name.split('.')[0] / 'bin',
    ]
    for exe_path in exe_paths:
        executable = exe_path / name
        if executable.exists():
            return executable

    path_str = ', '.join(str(path) for path in exe_paths)
    raise ValueError(f"{name} not found in {path_str}")


def _run_subprocess(name, *args, hide_stdout=False):
    executable = _find_executable(name)
    proc = subprocess.run([executable, *args], capture_output=True, text=True)

    stdout = proc.stdout
    if hide_stdout and proc.returncode == 0:
        stdout = ''

    return {name: Result(stdout, proc.stderr, proc.returncode)}


def lint_docker(path):
    results = {}
    results.update(_run_subprocess('hadolint', path))
    rulefile_path = ROOTDIR / 'dockerfile_lint_rules' / 'default_rules.yml'
    results.update(_run_subprocess('dockerfile_lint', '-r', rulefile_path, '-f', path))
    results.update(_run_subprocess('dockerlint.js', '-p', '-f', path))
    return results


def _check_yaml_syntax(path):
    with path.open('r') as f:
        try:
            yaml.full_load(f)
        except yaml.YAMLError as e:
            return Result(stdout=str(e), exitcode=1)
        return Result()


def _run_yamllint(path):
    yamllint_config = {
        'extends': 'default',
        'rules': {
            'document-start': 'disable',
        },
    }
    return _run_subprocess('yamllint', '--strict',
                           '-d', yaml.dump(yamllint_config), path)


def lint_compose(path):
    results = {'Basic syntax check': _check_yaml_syntax(path)}
    results.update(_run_yamllint(path))
    results.update(_run_subprocess('docker-compose', '-f', path, 'config', hide_stdout=True))
    return results


def lint_env(path):
    return _run_subprocess('dotenv-linter', path)
    