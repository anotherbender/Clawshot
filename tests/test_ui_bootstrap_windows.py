"""Run the shipped installer offline in Windows PowerShell 5.1, including inherited PS7 modules."""

import hashlib
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows PowerShell 5.1 regression")
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def uv_archive(tmp_path_factory):
    folder = tmp_path_factory.mktemp("synthetic-uv")
    source = folder / "Uv.cs"
    source.write_text('class Uv { static int Main() { System.Console.WriteLine("synthetic uv"); return 0; } }')
    compiler = Path(os.environ["SystemRoot"]) / "Microsoft.NET/Framework64/v4.0.30319/csc.exe"
    executable = folder / "uv.exe"
    subprocess.run([str(compiler), "/nologo", f"/out:{executable}", str(source)], check=True, capture_output=True)
    archive = folder / "uv.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.write(executable, "uv.exe")
    return archive, executable.read_bytes()


@pytest.mark.parametrize("modules", ["normal", "ps7"])
@pytest.mark.parametrize("valid", [True, False], ids=["verified", "corrupt"])
def test_installer_verifies_download_without_module_hash_cmdlet(tmp_path, uv_archive, modules, valid):
    powershell = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
    ps7_modules = Path(os.environ["ProgramFiles"]) / "PowerShell/7/Modules"
    if modules == "ps7" and not ps7_modules.is_dir():
        pytest.skip("PowerShell 7 modules are not installed")
    archive, executable = uv_archive
    expected = hashlib.sha256(archive.read_bytes()).hexdigest() if valid else "0" * 64
    scripts = tmp_path / "App with spaces/scripts"
    scripts.mkdir(parents=True)
    # Keep the shipped installer and pins, replacing only the transport and test archive's expected digest.
    prefix = (ROOT / "scripts/start-windows.ps1").read_text(encoding="ascii").split("$onPath =", 1)[0]
    command = prefix + """
function Invoke-WebRequest {
    param($Uri, $OutFile, $TimeoutSec, [switch]$UseBasicParsing)
    if ($Uri -notlike 'https://github.com/astral-sh/uv/releases/download/*') { throw 'Unexpected URL' }
    [IO.File]::Copy($env:TEST_UV_ARCHIVE, $OutFile)
}
$UvSha256['x86_64-pc-windows-msvc'] = $env:TEST_UV_DIGEST
$UvSha256['aarch64-pc-windows-msvc'] = $env:TEST_UV_DIGEST
Install-PinnedUv
& $UvExe --version
exit $LASTEXITCODE
"""
    script = scripts / "installer.ps1"
    script.write_text(command, encoding="ascii")
    normal = f"{Path(os.environ['ProgramFiles']) / 'WindowsPowerShell/Modules'};{powershell.parent / 'Modules'}"
    env = os.environ | {
        "PSModulePath": str(ps7_modules) if modules == "ps7" else normal,
        "TEST_UV_ARCHIVE": str(archive),
        "TEST_UV_DIGEST": expected,
    }
    result = subprocess.run(
        [str(powershell), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    installed = scripts.parent / ".tools/uv-0.13.7/uv.exe"
    diagnostic = (result.returncode, result.stdout, result.stderr)
    if valid:
        assert result.returncode == 0, diagnostic
        assert installed.read_bytes() == executable
        assert "synthetic uv" in result.stdout, diagnostic
    else:
        assert result.returncode == 1, diagnostic
        assert "SHA-256 differs" in result.stdout, diagnostic
        assert not installed.exists()
        assert "synthetic uv" not in result.stdout, diagnostic
    assert not list((scripts.parent / ".tools").glob("download-*"))
