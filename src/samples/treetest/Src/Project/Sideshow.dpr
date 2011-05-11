program Sideshow;

uses
  Forms,
  SideWindow in '..\SideWindow.pas' {Form1};

{$R *.res}

begin
  Application.Initialize;
  Application.CreateForm(TSideForm, SideForm);
  Application.Run;
end.
