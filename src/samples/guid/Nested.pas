program Nested;

procedure SayHi;
var
  X: String;

  function GetString: String;
  var
    Y: String;

    function GetTime: String;
    var
      Z: String;
    begin
      Z := 'now';
      Result := Z;
    end;

  begin
    Y := 'hi';
    Result := Y + ' ' + GetTime;
  end;

begin
  X := GetString;
  WriteLn('Saying ' + X);
end;

begin
  SayHi();
end.
