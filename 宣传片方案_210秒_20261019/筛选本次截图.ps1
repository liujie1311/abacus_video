$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$reviewRoot=Join-Path $PSScriptRoot '05_用户新截图筛选'
$archiveRoot=Join-Path $reviewRoot '原图留档_不代表选用'
$selectedRoot=Join-Path $reviewRoot '主选裁切'
New-Item -ItemType Directory -Path $archiveRoot,$selectedRoot -Force | Out-Null
$shotNames=@('59153cf8-9ad9-4213-b116-a98f1a1e42d8','2f532b75-ea8d-4a4b-94a1-2993af32651f','d113d271-1d2c-4604-8d28-141d8296e50f','b64599ca-c2c8-4e0d-874b-914d74cdd2bf','58deb658-7261-42b0-9e83-76be601009d3','4f6b5f6c-e951-467a-adee-e7736fa86a0b','2112f2d3-5488-4a58-9758-9c9a1eab8775','8119d133-0240-42eb-8cee-2e561c0fd2ff','1630ac6e-9fa9-4f4a-a53c-fd5b6e704786','ddb176b6-2b7b-43f1-979a-b84a959ea6fe','b471449e-bcff-41ae-a9d4-4d260769cda9','3bc3f531-511c-4bed-be96-4e2b00c67b07')
$titles=@('模板库','费米能模板','项目列表','项目内任务','能带流程','多层参数窗口','INPUT可视化配置','INPUT高级参数','PYATB空结果','工作流总览','任务日志','光学结果')
$verdicts=@('主选','备用','备用','主选','备用_宜放大补拍','暂不用','主选','暂不用_重复','暂不用_空结果','主选','备用','主选_独立物性示例')
$manifest=@()
for($i=0;$i -lt $shotNames.Count;$i++){
  $source=Join-Path $env:TEMP ('codex-clipboard-'+$shotNames[$i]+'.png')
  $name=('{0:D2}_' -f ($i+1))+$titles[$i]+'.png'
  $dest=Join-Path $archiveRoot $name
  Copy-Item -LiteralPath $source -Destination $dest -Force
  $manifest += [pscustomobject]@{number=$i+1;title=$titles[$i];verdict=$verdicts[$i];source=$source;archive=$dest;sha256=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash}
}
# Coordinates refer to the displayed 2048x1017 reference; convert to original pixels without enlargement.
$crops=@(
  @{number=1;rect=@(215,55,1815,880);label='01_模板库主画面'},
  @{number=4;rect=@(215,60,735,365);label='04_项目任务卡片'},
  @{number=7;rect=@(484,50,1081,909);label='07_INPUT配置弹窗'},
  @{number=10;rect=@(215,55,1815,870);label='10_工作流总览'},
  @{number=12;rect=@(830,574,555,432);label='12_光学结果图'}
)
foreach($crop in $crops){
  $src=[System.Drawing.Bitmap]::FromFile($manifest[$crop.number-1].archive)
  $r=$crop.rect
  $rect=New-Object System.Drawing.Rectangle([int]($r[0]*$src.Width/2048),[int]($r[1]*$src.Height/1017),[int]($r[2]*$src.Width/2048),[int]($r[3]*$src.Height/1017))
  $result=$src.Clone($rect,$src.PixelFormat)
  $output=Join-Path $selectedRoot ($crop.label+'.png')
  $result.Save($output,[System.Drawing.Imaging.ImageFormat]::Png)
  $crop.output=$output
  Write-Output ($crop.label+' '+$result.Width+'x'+$result.Height)
  $result.Dispose();$src.Dispose()
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $reviewRoot '原图来源与选择.json') -Encoding utf8
$crops | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $reviewRoot '裁切记录.json') -Encoding utf8
$canvas=New-Object System.Drawing.Bitmap(1600,1500)
$g=[System.Drawing.Graphics]::FromImage($canvas)
$g.Clear([System.Drawing.Color]::FromArgb(241,243,247))
$font=New-Object System.Drawing.Font('Microsoft YaHei',17)
$g.DrawString('本次主选：01 / 04 / 07 / 10 / 12',$font,[System.Drawing.Brushes]::Black,25,20)
$g.DrawString('裁切审看稿；未改内容、未放大原像素；并非全部成片镜头',$font,[System.Drawing.Brushes]::DimGray,25,60)
for($i=0;$i -lt $crops.Count;$i++){
  $x=25+($i%2)*790;$y=110+[Math]::Floor($i/2)*455
  $g.DrawString($crops[$i].label,$font,[System.Drawing.Brushes]::Black,$x,$y)
  $img=[System.Drawing.Image]::FromFile($crops[$i].output)
  $scale=[Math]::Min(750/$img.Width,395/$img.Height)
  $w=[int]($img.Width*$scale);$h=[int]($img.Height*$scale)
  $g.DrawImage($img,[int]($x+(750-$w)/2),[int]($y+40),$w,$h)
  $img.Dispose()
}
$g.DrawString('备用：02 / 03 / 05 / 11',$font,[System.Drawing.Brushes]::DarkSlateBlue,815,1050)
$g.DrawString('暂不用：06 / 08 / 09',$font,[System.Drawing.Brushes]::DarkRed,815,1110)
$canvas.Save((Join-Path $reviewRoot '主选裁切总览.jpg'),[System.Drawing.Imaging.ImageFormat]::Jpeg)
$g.Dispose();$canvas.Dispose();$font.Dispose()
