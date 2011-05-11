object FormMain: TFormMain
  Left = 0
  Top = 0
  Caption = 'PriceCheck'
  ClientHeight = 240
  ClientWidth = 311
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  PixelsPerInch = 96
  TextHeight = 13
  object BtnCheckPrice: TButton
    Left = 0
    Top = 207
    Width = 75
    Height = 33
    Caption = 'Check price!'
    TabOrder = 0
    OnClick = BtnCheckPriceClick
  end
  object MemoLog: TMemo
    Left = 0
    Top = 0
    Width = 313
    Height = 209
    ScrollBars = ssVertical
    TabOrder = 2
  end
  object BtnExit: TButton
    Left = 238
    Top = 207
    Width = 75
    Height = 33
    Caption = 'Exit'
    TabOrder = 1
    OnClick = BtnExitClick
  end
end
