unit FormMain;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, Env;

type
  TMainGui = class(TForm)
    BtnLoad: TButton;
    Multiline: TMemo;
    BtnQuit: TButton;
    procedure FormCreate(Sender: TObject);
    procedure BtnLoadClick(Sender: TObject);
    procedure BtnQuitClick(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  MainGui: TMainGui;

implementation

{$R *.dfm}

procedure TMainGui.BtnLoadClick(Sender: TObject);
var
  str : string;
begin
  str := Env.Get;
  Multiline.Text := str;
end;

procedure TMainGui.BtnQuitClick(Sender: TObject);
begin
  Application.Terminate;
end;

procedure TMainGui.FormCreate(Sender: TObject);
begin
  BtnLoadClick(Sender);
end;

end.
