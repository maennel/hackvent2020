import string
from typing import List

RIGHT = "right"
LEFT = "left"
UP = "up"
DOWN = "down"
FRONT = "front"
BACK = "back"


class Orientation:
    O_UP = "👆"
    O_RIGHT = "👉"
    O_DOWN = "👇"
    O_LEFT = "👈"

    CW = {
            O_UP: O_RIGHT,
            O_RIGHT: O_DOWN,
            O_DOWN: O_LEFT,
            O_LEFT: O_UP,
        }
    CC = {
            O_UP: O_LEFT,
            O_RIGHT: O_UP,
            O_DOWN: O_RIGHT,
            O_LEFT: O_DOWN,
        }
    FL = {
            O_UP: O_DOWN,
            O_DOWN: O_UP,
            O_LEFT: O_RIGHT,
            O_RIGHT: O_LEFT,
        }

    def __init__(self, value):
        assert (value in [self.O_UP, self.O_DOWN, self.O_LEFT, self.O_RIGHT])
        self.value = value

    def __str__(self):
        return self.value

    def cw(self):
        return Orientation(self.CW[self.value])

    def cc(self):
        return Orientation(self.CC[self.value])

    def fl(self):
        return Orientation(self.FL[self.value])


O_UP = Orientation(Orientation.O_UP)
O_RIGHT = Orientation(Orientation.O_RIGHT)
O_DOWN = Orientation(Orientation.O_DOWN)
O_LEFT = Orientation(Orientation.O_LEFT)

# 90 degree rotations in the XY plane. CW is clockwise, CC is counter-clockwise.
ROT_XY_CW = "rot_xy_cw"
ROT_XY_CC = "rot_xy_cc"

# 90 degree rotations in the XZ plane (around the y-axis when viewed pointing toward you).
ROT_XZ_CW = "rot_xz_cw"
ROT_XZ_CC = "rot_xz_cc"

# 90 degree rotations in the YZ plane (around the x-axis when viewed pointing toward you).
ROT_YZ_CW = "rot_yz_cw"
ROT_YZ_CC = "rot_yz_cc"


class OrientedCube:
    """Stores Pieces which are addressed through an x-y-z coordinate system:
        -x is the LEFT direction, +x is the RIGHT direction
        -y is the DOWN direction, +y is the UP direction
        -z is the BACK direction, +z is the FRONT direction
    """

    def __init__(self, orientations: List[Orientation]):
        """
        cube_str looks like:
                UUU                       0  1  2
                UUU                       3  4  5
                UUU                       6  7  8
            LLL FFF RRR BBB      9 10 11 12 13 14 15 16 17 18 19 20
            LLL FFF RRR BBB     21 22 23 24 25 26 27 28 29 30 31 32
            LLL FFF RRR BBB     33 34 35 36 37 38 39 40 41 42 43 44
                DDD                      45 46 47
                DDD                      48 49 50
                DDD                      51 52 53
        Note that the back side is mirrored in the horizontal axis during unfolding.
        Each 'sticker' must be a single character.
        """
        self.os= orientations

    def is_solved(self):
        return all([
            self._is_face_solved(f) for f in [FRONT, BACK, LEFT, RIGHT, DOWN, UP]
        ])

    def _is_face_solved(self, face):
        """
        Face is solved, if all fields have the same orientation
        :param face:
        :return:
        """
        return len(set([orientation.value for orientation in self._face(face)])) == 1

    def _face(self, face):
        """
        :param face: One of LEFT, RIGHT, UP, DOWN, FRONT, BACK
        :return: A list of Pieces on the given face
        """
        if face == FRONT:
            return self.os[12:15] + self.os[24:27] + self.os[36:39]
        elif face == UP:
            return self.os[0:9]
        elif face == DOWN:
            return self.os[45:54]
        elif face == LEFT:
            return self.os[9:12] + self.os[21:24] + self.os[33:36]
        elif face == RIGHT:
            return self.os[15:18] + self.os[27:30] + self.os[39:42]
        elif face == BACK:
            return self.os[18:21] + self.os[30:33] + self.os[42:45]

    def _rotate_face(self, face, rotation):
        self.rotate_orientations(rotation, face)

    # Rubik's Cube Notation: http://ruwix.com/the-rubiks-cube/notation/
    def L(self):
        self._rotate_face(LEFT, ROT_YZ_CW)
        return self

    def Li(self):
        self._rotate_face(LEFT, ROT_YZ_CC)
        return self

    def L2(self):
        self._rotate_face(LEFT, ROT_YZ_CW)
        self._rotate_face(LEFT, ROT_YZ_CW)
        return self

    def R(self):
        self._rotate_face(RIGHT, ROT_YZ_CW)
        return self

    def Ri(self):
        self._rotate_face(RIGHT, ROT_YZ_CC)
        return self

    def R2(self):
        self._rotate_face(RIGHT, ROT_YZ_CW)
        self._rotate_face(RIGHT, ROT_YZ_CW)
        return self

    def U(self):
        self._rotate_face(UP, ROT_XZ_CW)
        return self

    def Ui(self):
        self._rotate_face(UP, ROT_XZ_CC)
        return self

    def U2(self):
        self._rotate_face(UP, ROT_XZ_CW)
        self._rotate_face(UP, ROT_XZ_CW)
        return self

    def D(self):
        self._rotate_face(DOWN, ROT_XZ_CW)
        return self

    def Di(self):
        self._rotate_face(DOWN, ROT_XZ_CC)
        return self

    def D2(self):
        self._rotate_face(DOWN, ROT_XZ_CW)
        self._rotate_face(DOWN, ROT_XZ_CW)
        return self

    def F(self):
        self._rotate_face(FRONT, ROT_XY_CW)
        return self

    def Fi(self):
        self._rotate_face(FRONT, ROT_XY_CC)
        return self

    def F2(self):
        self._rotate_face(FRONT, ROT_XY_CW)
        self._rotate_face(FRONT, ROT_XY_CW)
        return self

    def B(self):
        self._rotate_face(BACK, ROT_XY_CW)
        return self

    def Bi(self):
        self._rotate_face(BACK, ROT_XY_CC)
        return self

    def B2(self):
        self._rotate_face(BACK, ROT_XY_CW)
        self._rotate_face(BACK, ROT_XY_CW)
        return self


    def sequence(self, move_str):
        """
        :param moves: A string containing notated moves separated by spaces: "L Ri U Ui B R2"
        """
        moves = [getattr(self, name) for name in move_str.split()]
        for move in moves:
            move()
        return self

    def flat_str(self):
        return "".join(x for x in str(self) if x not in string.whitespace)

    def __str__(self):
        template = ("    {}{}{}\n"
                    "    {}{}{}\n"
                    "    {}{}{}\n"
                    "{}{}{} {}{}{} {}{}{} {}{}{}\n"
                    "{}{}{} {}{}{} {}{}{} {}{}{}\n"
                    "{}{}{} {}{}{} {}{}{} {}{}{}\n"
                    "    {}{}{}\n"
                    "    {}{}{}\n"
                    "    {}{}{}")

        return "    " + template.format(*self.os).strip()

    def rotate_orientations(self, rotation, face):
        """
        os: orientations
                       0  1  2
                       3  4  5
                       6  7  8
              9 10 11 12 13 14 15 16 17 18 19 20
             21 22 23 24 25 26 27 28 29 30 31 32
             33 34 35 36 37 38 39 40 41 42 43 44
                      45 46 47
                      48 49 50
                      51 52 53

            Basis:
    return [
                                             os[0],       os[1],       os[2],
                                             os[3],       os[4],       os[5],
                                             os[6],       os[7],       os[8],
        os[9],      os[10],     os[11],      os[12],      os[13],      os[14],      os[15],      os[16],    os[17],    os[18],    os[19],      os[20],
        os[21],     os[22],     os[23],      os[24],      os[25],      os[26],      os[27],      os[28],    os[29],    os[30],    os[31],      os[32],
        os[33],     os[34],     os[35],      os[36],      os[37],      os[38],      os[39],      os[40],    os[41],    os[42],    os[43],      os[44],
                                             os[45],      os[46],      os[47],
                                             os[48],      os[49],      os[50],
                                             os[51],      os[52],      os[53]
    ]
        """

        if rotation == ROT_XY_CC:
            self.rotate_orientations(ROT_XY_CW, face)
            self.rotate_orientations(ROT_XY_CW, face)
            self.rotate_orientations(ROT_XY_CW, face)
        elif rotation == ROT_XZ_CC:
            self.rotate_orientations(ROT_XZ_CW, face)
            self.rotate_orientations(ROT_XZ_CW, face)
            self.rotate_orientations(ROT_XZ_CW, face)
        elif rotation == ROT_YZ_CC:
            self.rotate_orientations(ROT_YZ_CW, face)
            self.rotate_orientations(ROT_YZ_CW, face)
            self.rotate_orientations(ROT_YZ_CW, face)

        elif rotation == ROT_XY_CW and face == FRONT:
            os = self.os
            self.os = [
                                                      os[0],       os[1],       os[2],
                                                      os[3],       os[4],       os[5],
                                                      os[35].cw(), os[23].cw(), os[11].cw(),
                os[9],      os[10],     os[45].cw(), os[36].cw(), os[24].cw(), os[12].cw(), os[6].cw(), os[16],    os[17],    os[18],    os[19],      os[20],
                os[21],     os[22],     os[46].cw(), os[37].cw(), os[25].cw(), os[13].cw(), os[7].cw(), os[28],    os[29],    os[30],    os[31],      os[32],
                os[33],     os[34],     os[47].cw(), os[38].cw(), os[26].cw(), os[14].cw(), os[8].cw(), os[40],     os[41],    os[42],   os[43],      os[44],
                                                     os[39].cw(), os[27].cw(), os[15].cw(),
                                                     os[48],      os[49],      os[50],
                                                     os[51],      os[52],      os[53]
            ]
        elif rotation == ROT_XY_CW and face == BACK:
            os = self.os
            self.os = [
                                                    os[17].cc(), os[29].cc(), os[41].cc(),
                                                    os[3],       os[4],       os[5],
                                                    os[6],       os[7],       os[8],
                os[2].cc(), os[10],      os[11],    os[12],      os[13],      os[14],      os[15],      os[16],      os[53].cc(), os[42].cw(), os[30].cw(), os[18].cw(),
                os[1].cc(), os[22],      os[23],    os[24],      os[25],      os[26],      os[27],      os[28],      os[52].cc(), os[43].cw(), os[31].cw(), os[19].cw(),
                os[0].cc(), os[34],      os[35],    os[36],      os[37],      os[38],      os[39],      os[40],      os[51].cc(), os[44].cw(), os[32].cw(), os[20].cw(),
                                                    os[45],      os[46],      os[47],
                                                    os[48],      os[49],      os[50],
                                                    os[9].cc(), os[21].cc(), os[33].cc()
            ]
        elif rotation == ROT_XZ_CW and face == UP:
            os = self.os
            self.os = [
                                                     os[6].cw(),  os[3].cw(),  os[0].cw(),
                                                     os[7].cw(),  os[4].cw(),  os[1].cw(),
                                                     os[8].cw(),  os[5].cw(),  os[2].cw(),
                os[12],      os[13],    os[14],      os[15],      os[16],      os[17],      os[18],      os[19],    os[20],     os[9],      os[10],     os[11],
                os[21],     os[22],     os[23],      os[24],      os[25],      os[26],      os[27],      os[28],    os[29],    os[30],    os[31],      os[32],
                os[33],     os[34],     os[35],      os[36],      os[37],      os[38],      os[39],      os[40],    os[41],    os[42],    os[43],      os[44],
                                                     os[45],      os[46],      os[47],
                                                     os[48],      os[49],      os[50],
                                                     os[51],      os[52],      os[53]
            ]
        elif rotation == ROT_XZ_CW and face==DOWN:
            os = self.os
            self.os = [
                                             os[0],       os[1],       os[2],
                                             os[3],       os[4],       os[5],
                                             os[6],       os[7],       os[8],
        os[9],      os[10],     os[11],      os[12],      os[13],      os[14],      os[15],      os[16],    os[17],    os[18],    os[19],      os[20],
        os[21],     os[22],     os[23],      os[24],      os[25],      os[26],      os[27],      os[28],    os[29],    os[30],    os[31],      os[32],
        os[42],    os[43],      os[44],      os[33],      os[34],      os[35],      os[36],      os[37],    os[38],    os[39],    os[40],      os[41],
                                             os[51].cw(), os[48].cw(), os[45].cw(),
                                             os[52].cw(), os[49].cw(), os[46].cw(),
                                             os[53].cw(), os[50].cw(), os[47].cw()
            ]
        elif rotation == ROT_YZ_CW and face == LEFT:
            os = self.os
            self.os = [
                                             os[44].fl(),os[1],       os[2],
                                             os[32].fl(),os[4],       os[5],
                                             os[20].fl(),os[7],       os[8],
        os[33].cw(), os[21].cw(),os[9].cw(), os[0],      os[13],      os[14],      os[15],      os[16],    os[17],    os[18],    os[19],      os[51].fl(),
        os[34].cw(),os[22].cw(),os[10].cw(), os[3],      os[25],      os[26],      os[27],      os[28],    os[29],    os[30],    os[31],      os[48].fl(),
        os[35].cw(),os[23].cw(),os[11].cw(), os[6],      os[37],      os[38],      os[39],      os[40],    os[41],    os[42],    os[43],      os[45].fl(),
                                             os[12],      os[46],      os[47],
                                             os[24],      os[49],      os[50],
                                             os[36],      os[52],      os[53]
            ]
        elif rotation == ROT_YZ_CW and face == RIGHT:
            os = self.os
            self.os = [
                                             os[0],       os[1],       os[14],
                                             os[3],       os[4],       os[26],
                                             os[6],       os[7],       os[38],
        os[9],      os[10],     os[11],      os[12],      os[13],      os[47],      os[39].cw(),  os[27].cw(),os[15].cw(),os[8].fl(),    os[19],      os[20],
        os[21],     os[22],     os[23],      os[24],      os[25],      os[50],      os[40].cw(),  os[28].cw(),os[16].cw(),os[5].fl(),    os[31],      os[32],
        os[33],     os[34],     os[35],      os[36],      os[37],      os[53],      os[41].cw(),  os[29].cw(),os[17].cw(),os[2].fl(),    os[43],      os[44],
                                             os[45],      os[46],      os[42].fl(),
                                             os[48],      os[49],      os[30].fl(),
                                             os[51],      os[52],      os[18].fl()
            ]
        else:
            raise ValueError("Rotation %s and face %s are not supported." % (rotation, face))
