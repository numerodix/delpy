program GuiTest;

uses
  Forms,
  FormMain in 'FormMain.pas' {MainGui},
  Env in 'Env.pas';

{$R *.res}

begin
  Application.Initialize;
  Application.Title := 'GuiTest';
  Application.CreateForm(TMainGui, MainGui);
  Application.Run;
end.
