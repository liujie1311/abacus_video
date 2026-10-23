$ErrorActionPreference = 'Stop'
$platformEvidence = Join-Path $PSScriptRoot '平台核查'
New-Item -ItemType Directory -Path $platformEvidence -Force | Out-Null
$platformPages = @{
  dashboard = '/src/views/dashboard/index.vue'
  projects = '/src/views/projects/list.vue'
  project_detail = '/src/views/projects/detail.vue'
  templates = '/src/views/templates/index.vue'
  template_detail = '/src/views/templates/detail.vue'
  workflows = '/src/views/workflows/index.vue'
  workflow_detail = '/src/views/workflows/detail.vue'
  toolbox = '/src/views/toolbox/index.vue'
  events = '/src/views/events/index.vue'
  manual = '/src/views/manual/index.vue'
}
foreach ($entry in $platformPages.GetEnumerator()) {
  try {
    $response = (Invoke-WebRequest -Uri ('http://localhost:8080' + $entry.Value) -UseBasicParsing -TimeoutSec 15).Content
    $marker = '//# sourceMappingURL=data:application/json;base64,'
    $offset = $response.LastIndexOf($marker)
    if ($offset -ge 0) {
      $encoded = $response.Substring($offset + $marker.Length).Trim()
      $map = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($encoded)) | ConvertFrom-Json
      $source = $map.sourcesContent -join "`n"
    } else {
      $source = $response
    }
    Set-Content -LiteralPath (Join-Path $platformEvidence ($entry.Key + '.txt')) -Value $source -Encoding utf8
    Write-Output ($entry.Key + ' saved ' + $source.Length + ' characters')
  } catch {
    Write-Output ($entry.Key + ' FAILED: ' + $_.Exception.Message)
  }
}
