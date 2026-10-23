$ErrorActionPreference = 'Stop'
$shotRoot = Join-Path $PSScriptRoot '04_平台截图素材'
$manualRoot = Join-Path $shotRoot '用户手册历史截图'
$existingRoot = Join-Path $shotRoot '已有原始截图'
New-Item -ItemType Directory -Path $manualRoot,$existingRoot -Force | Out-Null
$shots = @(
  @('01_项目管理','image-20260616144129243.png'),
  @('02_项目内任务','image-20260616144318250.png'),
  @('03_模板库','image-20260616144401699.png'),
  @('04_模板详情','image-20260616144424743.png'),
  @('05_工作流列表','image-20260616144442673.png'),
  @('06_工作流详情','image-20260616144506390.png'),
  @('07_任务输出','image-20260616144513485.png'),
  @('08_结构转换','image-20260616144813384.png'),
  @('09_输入配置','image-20260616144844969.png'),
  @('10_能带绘制','image-20260616144925862.png'),
  @('11_态密度绘制','image-20260616145135642.png'),
  @('12_结构展示','image-20260616145323368.png')
)
$manifest = @()
foreach($shot in $shots){
  $url = 'http://localhost:8080/src/views/manual/使用手册/images/' + $shot[1]
  $dest = Join-Path $manualRoot ($shot[0]+'.png')
  Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 20 -OutFile $dest
  $manifest += [pscustomobject]@{name=$shot[0];file=('用户手册历史截图/'+$shot[0]+'.png');source=$url;status='网站手册历史截图；不是本次实时截屏'}
  Write-Output ($shot[0]+' 已提取')
}
$workspaceRoot = Split-Path $PSScriptRoot -Parent
$existingShots = @(
  @('01_已有首页.png','交付_V10_60秒_去小字_更新平台画面/03_素材/原始素材/新平台首页_用户图三.png'),
  @('02_已有模板库.png','交付_V3_含模板_无字幕/03_图片素材/03_原始截图/模板库全景_3450x1701.png'),
  @('03_已有执行状态.png','交付_V6_80秒审看版/03_素材/原始素材/金属熔点_工作流执行状态_原图.png')
)
foreach($shot in $existingShots){
  $source=Join-Path $workspaceRoot $shot[1]
  Copy-Item -LiteralPath $source -Destination (Join-Path $existingRoot $shot[0]) -Force
  $manifest += [pscustomobject]@{name=$shot[0];file=('已有原始截图/'+$shot[0]);source=$source;status='既有文件复制；不是本次实时截屏'}
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $shotRoot '素材来源.json') -Encoding utf8

Add-Type -AssemblyName System.Drawing
$canvas = New-Object System.Drawing.Bitmap(1600,1800)
$graphics = [System.Drawing.Graphics]::FromImage($canvas)
$graphics.Clear([System.Drawing.Color]::FromArgb(240,242,246))
$font = New-Object System.Drawing.Font('Microsoft YaHei',15)
$titleFont = New-Object System.Drawing.Font('Microsoft YaHei',22)
$graphics.DrawString('平台素材总览 — 用户手册历史截图',[System.Drawing.Font]$titleFont,[System.Drawing.Brushes]::Black,25,15)
$graphics.DrawString('仅供选图核对；未采集当前登录后的界面',[System.Drawing.Font]$font,[System.Drawing.Brushes]::DarkRed,25,62)
for($i=0;$i -lt $shots.Count;$i++){
  $img=[System.Drawing.Image]::FromFile((Join-Path $manualRoot ($shots[$i][0]+'.png')))
  $x=20+($i%3)*530
  $y=110+[Math]::Floor($i/3)*420
  $graphics.DrawString($shots[$i][0]+'  '+$img.Width+'x'+$img.Height,$font,[System.Drawing.Brushes]::Black,$x,$y)
  $scale=[Math]::Min(510/$img.Width,365/$img.Height)
  $w=[int]($img.Width*$scale);$h=[int]($img.Height*$scale)
  $graphics.DrawImage($img,[int]($x+(510-$w)/2),[int]($y+38),$w,$h)
  $img.Dispose()
}
$canvas.Save((Join-Path $shotRoot '截图总览_历史素材.jpg'),[System.Drawing.Imaging.ImageFormat]::Jpeg)
$graphics.Dispose();$canvas.Dispose();$font.Dispose();$titleFont.Dispose()
$cards=($manifest | ForEach-Object { '<article><h2>'+[System.Net.WebUtility]::HtmlEncode($_.name)+'</h2><p>'+[System.Net.WebUtility]::HtmlEncode($_.status)+'</p><a href="'+$_.file+'"><img loading="lazy" src="'+$_.file+'"></a></article>' }) -join "`n"
$html='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>平台截图素材</title><style>body{font-family:Arial,sans-serif;margin:32px;background:#f1f3f6;color:#18202d}main{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}article{padding:20px;background:white;border-radius:12px}h2{font-size:20px}p{color:#9b302f}img{max-width:100%;height:auto}</style><h1>平台截图素材</h1><p>以下均为历史素材；不代表本次已完成当前版本截图采集。点击图片可查看原图。</p><main>'+$cards+'</main></html>'
$html | Set-Content -LiteralPath (Join-Path $shotRoot '素材画廊.html') -Encoding utf8
Write-Output ('已整理 '+$manifest.Count+' 张，已生成总览与来源清单')
