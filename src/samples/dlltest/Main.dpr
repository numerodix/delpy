program Main;

{$APPTYPE CONSOLE}

uses
  Windows,
  ShareMem,
  SysUtils,
  LibIndex;

function Min(X, Y: Integer): Integer; stdcall; external 'LibMin.dll';

var
  X, Y, A, B: Integer;
  Handle: THandle;
  Max: function(X, Y: Integer): Integer; stdcall;
begin
  X := 1;
  Y := -1;
  B := 0;

  System.WriteLn('Loaded statically : ' + LibIndex.LibMin);
  A := Min(X, Y);

  Handle := LoadLibrary(LibIndex.LibMax);
  System.WriteLn('Loaded dynamically: ' + LibIndex.LibMax);

  if Handle <> 0 then
    begin
      @Max := GetProcAddress(Handle, 'Max');
      if @Max <> nil then
        begin
          B := Max(X, Y);
        end;
      FreeLibrary(Handle);
    end; 

  System.WriteLn('');

  System.Writeln(
    'Min('
    + IntToStr(X)
    + ', '
    + IntToStr(Y)
    + '): '
    + IntToStr(A)
    );
  System.Writeln(
    'Max('
    + IntToStr(X)
    + ', '
    + IntToStr(Y)
    + '): '
    + IntToStr(B)
    );
end.
