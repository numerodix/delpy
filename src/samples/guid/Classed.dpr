program Classed;

type
  TMyClass = class
    published
      function GetCount: Integer;
      function DoNothing: Integer;
      property Count: Integer read GetCount;
  end;


function Top: Integer;
begin
end;

function TMyClass.GetCount: Integer;
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
