program Classed;

type
  TMyClass = class
    published
      class function GetCount: Integer;
      function DoNothing: Integer;
  end;


function Top: Integer;
begin
end;

class function TMyClass.GetCount: Integer;
begin
  Result := 1;
end;

function TMyClass.DoNothing: Integer;
begin
  Result := 2;
end;

var
  MyClass: TMyClass;


begin
  MyClass := TMyClass.Create;
  WriteLn(MyClass.DoNothing( ));
end.
