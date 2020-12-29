# HV20.07 Bad morals

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | kuyaya |
| **Level**      | medium |
| **Categories** | `reverse engineering`, `programming` |

## Description

One of the elves recently took a programming 101 course. Trying to be helpful, he implemented a program for Santa to generate all the flags for him for this year's HACKvent 2020. The problem is, he can't remember how to use the program any more and the link to the documentation just says `404 Not found`. I bet he learned that in the Programming 101 class as well.

Can you help him get the flag back?

[BadMorals.exe](./cc1b4db7-d5b6-48b8-bee5-8dcba508bf81.exe)

### Hints
There are nearly infinite inputs that pass almost all the tests in the program.
For the correct flag, the final test has to be successful as well.

## Approach

Analysing the file hinted that it was a Mono/.Net file:
```bash
$ file cc1b4db7-d5b6-48b8-bee5-8dcba508bf81.exe 
cc1b4db7-d5b6-48b8-bee5-8dcba508bf81.exe: PE32 executable (console) Intel 80386 Mono/.Net assembly, for MS Windows
```

Searching for a decompiler for such files resulted in finding [ILSpy](https://github.com/icsharpcode/ILSpy). A variant with a frontend for Linux is provided by [AvaloniaILSpy](https://github.com/icsharpcode/AvaloniaILSpy).

The decompiled code (Main) looks as follows (slightly shortened for brevity):
```cs
public static void Main(string[] args)
{
	try
	{
		Console.Write("Your first input: ");
		char[] array = Console.ReadLine().ToCharArray();
		string text = "";
		string text2 = "";
		for (int i = 0; i < array.Length; i++)
		{
			if (i % 2 == 0 && i + 2 <= array.Length)
			{
				text += array[i + 1].ToString();
			}
		}
		if (text == "BumBumWithTheTumTum")
		{
			text2 = "SFYyMH" + array[17].ToString() + "yMz" + array[8].GetHashCode() % 10 + "zcnMzXzN" + array[3].ToString() + "ZzF" + array[9].ToString() + "MzNyM" + array[13].ToString() + "5n" + array[14].ToString() + "2";
			goto IL_0141;
		}
		if (!(text == ""))
		{
			text2 = text;
			goto IL_0141;
		}
		Console.WriteLine("Your input is not allowed to result in an empty string");
		goto end_IL_0000;
		IL_0141:
		Console.Write("Your second input: ");
		char[] array2 = Console.ReadLine().ToCharArray();
		text = "";
		string text3 = "";
		Array.Reverse(array2);
		for (int j = 0; j < array2.Length; j++)
		{
			text += array2[j].ToString();
		}
		if (text == "BackAndForth")
		{
			text3 = "Q1RGX3" + array2[11].ToString() + "sNH" + array2[8].ToString() + "xbm" + array2[5].ToString() + "f";
			goto IL_021c;
		}
		if (!(text == ""))
		{
			text3 = text;
			goto IL_021c;
		}
		Console.WriteLine("Your input is not allowed to result in an empty string");
		goto end_IL_0000;
		IL_021c:
		Console.Write("Your third input: ");
		char[] array3 = Console.ReadLine().ToCharArray();
		text = "";
		string text4 = "";
		byte b = 42;
		for (int k = 0; k < array3.Length; k++)
		{
			char c = (char)(array3[k] ^ b);
			b = (byte)(b + k - 4);
			text += c.ToString();
		}
		if (text == "DinosAreLit")
		{
			text4 = "00ZD" + array3[3].ToString() + "f" + array3[2].ToString() + "zRzeX0=";
			goto IL_02e9;
		}
		if (!(text == ""))
		{
			text4 = text;
			goto IL_02e9;
		}
		Console.WriteLine("Your input is not allowed to result in an empty string");
		goto end_IL_0000;
		IL_02e9:
		byte[] array4 = Convert.FromBase64String(text2 + text4);
		byte[] array5 = Convert.FromBase64String(text3);
		byte[] array6 = new byte[array4.Length];
		for (int l = 0; l < array4.Length; l++)
		{
			array6[l] = (byte)(array4[l] ^ array5[l % array5.Length]);
		}
		byte[] array7 = SHA1.Create().ComputeHash(array6);
		byte[] array8 = new byte[20]
		{
			107, 64, 119, 202, 154, 218, 200, 113, 1, 66, 148, 207, 23, 254, 198, 197, 79, 21, 10
		};
		for (int m = 0; m < array7.Length; m++)
		{
			if (array7[m] != array8[m])
			{
				Console.WriteLine("Your inputs do not result in the flag.");
				return;
			}
		}
		string @string = Encoding.ASCII.GetString(array4);
		if (@string.StartsWith("HV20{"))
		{
			Console.WriteLine("Congratulations! You're now worthy to claim your flag: {0}", @string);
		}
		end_IL_0000:;
	}
	catch
	{
		Console.WriteLine("Please try again.");
	}
	finally
	{
		Console.WriteLine("Press enter to exit.");
		Console.ReadLine();
	}
}
```

For all three inputs, most of the characters were easily revertable. So, we ended up with a base64 string with 2 unknown positions: `SFYyMHtyMz{}zcnMzXzNuZzFuMzNyMW5n{}200ZDNfMzRzeX0=`.

At first, one is tempted to try through possibilities manually, as for the first missing characters only chars `0` through `9` were possible. All flag submissions failed, though...

I therefore wrote a small solver script to check for the hash indicated in the source file:
```python
import base64
from hashlib import sha1

for a in range(0, 9):
    for b in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/":
        try:
            flag = base64.b64decode("SFYyMHtyMz{}zcnMzXzNuZzFuMzNyMW5n{}200ZDNfMzRzeX0=".format(a, b))
        except UnicodeDecodeError:
            print("Error with a={} and b={}".format(a, b))
            continue
        key = base64.b64decode("Q1RGX3hsNHoxbmnf")
        arr = bytearray()

        for i in range(0, len(flag)):
            arr.append(flag[i] ^ key[i % len(key)])

        if "6b4077ca9adac8713f014294cf17fec6c54f150a" == sha1(arr).hexdigest():
            print(flag)
            print("Success with a={} and b={}".format(a, b))
```

The missing characters to produce the right flag were `a=8` and `b=X`:
```python
'SFYyMHtyMz{}zcnMzXzNuZzFuMzNyMW5n{}200ZDNfMzRzeX0='.format(8, X)
```

## Tools
- [ILSpy](https://github.com/icsharpcode/AvaloniaILSpy/releases/tag/v5.0-rc2) - a decompiler for .NET (Mono) code (very happy I used this one)
- CyberChef - did not bring the breakthrough
- Python

## Flag
`HV20{r3?3rs3_3ng1n33r1ng_m4d3_34sy}`

## Credits
To *The Compiler* for confirming I'm on the right track it was only my implementation that was wrong.
