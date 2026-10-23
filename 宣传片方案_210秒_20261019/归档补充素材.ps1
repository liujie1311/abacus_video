$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$bundleRoot=Join-Path $PSScriptRoot '06_补充素材与AI复核'
$originalRoot=Join-Path $bundleRoot '原图'
New-Item -ItemType Directory -Path $originalRoot -Force | Out-Null
$projectRoot=Split-Path $PSScriptRoot -Parent
$sourceRoot=Split-Path $projectRoot -Parent
$entries=@(
  @('N01_平台首页',(Join-Path $env:TEMP 'codex-clipboard-07e41597-43e5-4dc0-a5f0-37ffcbe9afe3.png'),'本次补充'),
  @('N02_PYATB生成结果',(Join-Path $env:TEMP 'codex-clipboard-e4612f6a-872e-418f-a8a4-32f11ce2b68b.png'),'本次补充'),
  @('N03_PDOS绘图结果',(Join-Path $env:TEMP 'codex-clipboard-844b995a-091d-4e09-8365-b5d3c99e8c7a.png'),'本次补充'),
  @('A01_AI提问',(Join-Path $sourceRoot '16e10cf0-f4ca-4407-8d2a-8cb7321086a3.png'),'已有原始素材'),
  @('A02_AI完成与绘图链接',(Join-Path $sourceRoot 'cebe4c78-afcb-4bee-b8f8-31b2271a2cb9.png'),'已有原始素材'),
  @('A03_MSD原始曲线',(Join-Path $sourceRoot '0252131c-9fe3-48d6-9f17-739ffb635336.png'),'已有原始素材'),
  @('A04_AI分析与建议',(Join-Path $sourceRoot '17ca551a-694e-46b7-8861-0ff29629ef79.png'),'已有原始素材')
)
$manifest=@()
foreach($entry in $entries){
  $dest=Join-Path $originalRoot ($entry[0]+'.png')
  Copy-Item -LiteralPath $entry[1] -Destination $dest -Force
  $img=[System.Drawing.Image]::FromFile($dest)
  $manifest += [pscustomobject]@{name=$entry[0];source=$entry[1];kind=$entry[2];file=$dest;width=$img.Width;height=$img.Height;sha256=(Get-FileHash -LiteralPath $dest).Hash}
  $img.Dispose()
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $bundleRoot '来源清单.json') -Encoding utf8
$canvas=New-Object System.Drawing.Bitmap(1600,1800)
$g=[System.Drawing.Graphics]::FromImage($canvas)
$g.Clear([System.Drawing.Color]::FromArgb(241,243,247))
$font=New-Object System.Drawing.Font('Microsoft YaHei',16)
$g.DrawString('新增平台素材与已找回的AI原图',$font,[System.Drawing.Brushes]::Black,25,20)
$g.DrawString('内容审看总览；正式剪辑仅使用必要局部',$font,[System.Drawing.Brushes]::DimGray,25,55)
for($i=0;$i -lt $manifest.Count;$i++){
  $entry=$manifest[$i];$x=25+($i%2)*790;$y=100+[Math]::Floor($i/2)*420
  $g.DrawString($entry.name+' · '+$entry.kind,$font,[System.Drawing.Brushes]::Black,$x,$y)
  $img=[System.Drawing.Image]::FromFile($entry.file)
  $scale=[Math]::Min(750/$img.Width,365/$img.Height)
  $w=[int]($img.Width*$scale);$h=[int]($img.Height*$scale)
  $g.DrawImage($img,[int]($x+(750-$w)/2),[int]($y+38),$w,$h)
  $img.Dispose()
}
$canvas.Save((Join-Path $bundleRoot '素材复核总览.jpg'),[System.Drawing.Imaging.ImageFormat]::Jpeg)
$g.Dispose();$canvas.Dispose();$font.Dispose()
Write-Output ('归档原图 '+$manifest.Count+' 张')
$manifest | Select-Object name,width,height | Format-Table
