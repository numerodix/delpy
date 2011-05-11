program TryAsm;

uses

  Windows,

  Classes, SysUtils, Messages;

function LoCase(C: AnsiChar) : AnsiChar;
asm
  and   eax, 0FFh
  push  eax
  call  CharLower
end;

var
  C: AnsiChar;
begin
  C := 'B';
  WriteLn(LoCase(C));
end.
