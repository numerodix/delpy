// Copyright: Martin Matusiak <numerodix@gmail.com>
// Licensed under the GNU Public License, version 3.

program DfmToBinary;

{$APPTYPE CONSOLE}

uses
  Classes,
  SysUtils;

{ ref: http://www.delphidabbler.com/tips/66 }

{ returns true if dfm file is in a binary format }
function DfmIsBinary(FileName: string): Boolean;
var
  FileStream: TFileStream;
  B: Byte;
begin
  B := 0;
  FileStream := TFileStream.Create(FileName, fmOpenRead);
  try
    FileStream.Read( B, 1 );
    Result := B = $FF;
  finally
    FileStream.Free;
  end;
end;

{ convert a binary dfm file to a text dfm file }
function Dfm2Txt(Src, Dest: string): Boolean;
var
  SrcS, DestS: TFileStream;
begin
  System.WriteLn('> Converting from binary to text: '
    + Src + ' -> ' + Dest);

  SrcS := TFileStream.Create(Src, fmOpenRead);
  DestS := TFileStream.Create(Dest, fmCreate);

  try
    try
      ObjectResourceToText(SrcS, DestS);
      if FileExists(Src) and FileExists(Dest) then
        Result := True
      else
        Result := False;
    except
      Result := False;
    end;
  finally
    SrcS.Free;
    DestS.Free;
  end;
end;

{ convert a text Dfm file to a binary Dfm file }
function Txt2Dfm(Src, Dest: string): boolean;
var
  SrcS, DestS: TFileStream;
begin
  System.WriteLn('> Converting from text to binary: '
    + Src + ' -> ' + Dest);

  SrcS := TFileStream.Create(Src, fmOpenRead);
  DestS := TFileStream.Create(Dest, fmCreate);

  try
    try
      ObjectTextToResource(SrcS, DestS);
      if FileExists(Src) and FileExists(Dest) then
        Result := True
      else
        Result := False;
    except
      Result := False;
    end;
  finally
    SrcS.Free;
    DestS.Free;
  end;
end;


var
  Exit: Boolean;
  Action: string;
  Src, Dest: string;
begin
  if ParamCount < 4 then
    begin
      System.WriteLn('Usage:  ' + ParamStr(0));
      System.WriteLn( '          [--to-binary|--to-text] Form.txt.dfm');
      System.WriteLn( '           --output               Form.bin.dfm');
      ExitCode := 1;
      Halt;
    end;

  Action := ParamStr(1);
  Src := ParamStr(2);
  Dest := ParamStr(4);

  if Src = Dest then
  begin
    System.WriteLn('Error: Source and target file are the same');
    ExitCode := 1;
    Halt;
  end;

  Exit := True;
  { text to binary }
  if Action = '--to-binary' then
    begin
      if not DfmIsBinary(Src) then
        Exit := Txt2Dfm(Src, Dest);
    end

  else if Action = '--to-text' then
    begin
      if DfmIsBinary(Src) then
        Exit := Dfm2Txt(Src, Dest);
    end;

  if not Exit then
  begin
    System.WriteLn('Error: Conversion failed');
    ExitCode := 1;
  end;
end.
