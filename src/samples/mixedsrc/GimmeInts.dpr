program GimmeInts;

{$APPTYPE CONSOLE}

{$R *.res}

uses
  SysUtils,
  SrcUnit in 'SrcUnit.pas',
  CompiledUnit in 'CompiledUnit.pas';

var
  x,y : Integer;
begin
  x := SrcUnit.Gimme();
  y := CompiledUnit.Gimme();
  System.Writeln('SrcUnit.Gimme()      : ' + IntToStr(x));
  System.Writeln('CompiledUnit.Gimme() : ' + IntToStr(y));
end.
