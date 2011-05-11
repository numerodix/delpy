unit SideWindow;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls;

type
  TSideForm = class(TForm)
    Lbl: TLabel;
    procedure FormCreate(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  SideForm: TSideForm;

implementation

{$R *.dfm}

uses
	Lib;

procedure TSideForm.FormCreate(Sender: TObject);
begin
  Lbl.Caption := 'I''m v' + Lib.version;
end;

end.
