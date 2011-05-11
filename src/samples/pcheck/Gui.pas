unit Gui;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls,
  Core;

type
  TFormMain = class(TForm)
    BtnCheckPrice: TButton;
    MemoLog: TMemo;
    BtnExit: TButton;
    procedure BtnExitClick(Sender: TObject);
    procedure BtnCheckPriceClick(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  FormMain: TFormMain;

implementation

{$R *.dfm}

procedure TFormMain.BtnCheckPriceClick(Sender: TObject);
var
  price, taxrate, salesprice: integer;
  product1, product2: Core.TProduct;
  products: Core.TProducts;
  i: integer;
  company1, company2, company3: Core.TCompany;
begin
  { #remote }
  price := Core.GetPrice;

  { #remote }
  taxrate := Core.GetTaxRate;

  { #remote }
  salesprice := Core.ComputePrice(price, taxrate);

  MemoLog.Lines.Append(IntToStr(price) + ' + ' + IntToStr(taxrate) + '% = ' +
      IntToStr(salesprice));



  product1 := Core.MakeProduct('Magnet, white', salesprice);

  MemoLog.Lines.Append(' * ' + product1.Name + ': ' + IntToStr(product1.Price));



  products := Core.MakeProducts;

  for i := Low(products) to High(products) do
    MemoLog.Lines.Append(' ' + IntToStr(i) + '. ' + products[i].Name + ': ' + IntToStr(products[i].Price));



  company1 := Core.TCompany.Create('Acme', product1);

  Core.Tradeshow.Register(company1);

  product2 := Core.MakeProduct('Screwdriver', 290);
  company2 := Core.TCompany.Create('Abysmal', product2);

  Core.Tradeshow.Register(company2);

  company3 := Core.Tradeshow.Find('Acme');

  MemoLog.Lines.Append(company3.Print);

end;

procedure TFormMain.BtnExitClick(Sender: TObject);
begin
  Self.Close;
end;

end.
