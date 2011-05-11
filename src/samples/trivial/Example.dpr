program Abysmal;

uses
  Forms,
  FormMain in 'FormMain.pas' {MainGui},
  Env in 'Env.pas';

{$R *.res}
{$R '..\Source\SynEditReg.dcr'}
{$R 'UserControls\ucMenu.TucMenu.resources' 'UserControls\ucMenu.resx'}

begin
  Application.Initialize;
  Application.Title := 'Abysmal';
  Application.CreateForm(TMainGui, MainGui);
  Application.Run;
end.
