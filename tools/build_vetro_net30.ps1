$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot
$referenceRoot = Join-Path $PSScriptRoot 'netcore30-ref/package/ref/netcoreapp3.0'
$outputRoot = Join-Path $taskRoot 'research/tizen55-port/payload'
New-Item -ItemType Directory -Force $outputRoot | Out-Null
Add-Type -Path (Join-Path $PSHOME 'Microsoft.CodeAnalysis.dll')
Add-Type -Path (Join-Path $PSHOME 'Microsoft.CodeAnalysis.CSharp.dll')
$references = [Microsoft.CodeAnalysis.MetadataReference[]]@(Get-ChildItem $referenceRoot -Filter '*.dll' | ForEach-Object {
    [Microsoft.CodeAnalysis.MetadataReference]::CreateFromFile($_.FullName)
})
$common = Join-Path $taskRoot 'research/vetro/rooting/tools/samsung-tv-root-master/payloads/common'
$sources = @{
    HelperSmokeProbe = Join-Path $taskRoot 'research/tizen55-port/HelperSmokeProbe.cs'
    DriverProbe = Join-Path $taskRoot 'research/tizen55-port/DriverProbe.cs'
    RuntimeProbe = Join-Path $taskRoot 'research/tizen55-port/RuntimeProbe.cs'
    SamsungTvArchiveRoot = Join-Path $common 'SamsungTvArchiveRoot.cs'
    SamsungTvRootAgent = Join-Path $common 'SamsungTvRootAgent.cs'
    SamsungTvRemoteInputAgent = Join-Path $taskRoot 'research/vetro/rooting/payload/SamsungTvRemoteInputAgent.cs'
    TvState = Join-Path $taskRoot 'research/vetro/app/native/TvState.cs'
    CapabilityProbe = Join-Path $taskRoot 'research/CapabilityProbe.cs'
}
foreach ($name in $sources.Keys) {
    $tree = [Microsoft.CodeAnalysis.CSharp.CSharpSyntaxTree]::ParseText([IO.File]::ReadAllText($sources[$name]))
    $options = [Microsoft.CodeAnalysis.CSharp.CSharpCompilationOptions]::new([Microsoft.CodeAnalysis.OutputKind]::ConsoleApplication)
    $options = $options.WithOptimizationLevel([Microsoft.CodeAnalysis.OptimizationLevel]::Release).WithDeterministic($true)
    $compilation = [Microsoft.CodeAnalysis.CSharp.CSharpCompilation]::Create($name, [Microsoft.CodeAnalysis.SyntaxTree[]]@($tree), $references, $options)
    $outputPath = Join-Path $outputRoot "$name.dll"
    $stream = [IO.File]::Create($outputPath)
    try { $result = $compilation.Emit($stream) } finally { $stream.Dispose() }
    if (-not $result.Success) { throw ($result.Diagnostics -join "`n") }
    $config = '{"runtimeOptions":{"tfm":"netcoreapp3.0","framework":{"name":"Microsoft.NETCore.App","version":"3.0.0"}}}'
    [IO.File]::WriteAllText((Join-Path $outputRoot "$name.runtimeconfig.json"), $config)
    Write-Output "Built $name for .NET Core 3.0"
}
