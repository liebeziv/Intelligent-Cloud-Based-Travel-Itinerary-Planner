param(
    [Parameter(Mandatory)] [string]$Region,
    [Parameter(Mandatory)] [string]$EbApplicationName,
    [Parameter(Mandatory)] [string]$EbEnvironmentName,
    [Parameter(Mandatory)] [string]$EbDeploymentBucket,
    [Parameter(Mandatory)] [string]$FrontendBucket,
    [Parameter(Mandatory)] [string]$CloudFrontDistributionId,
    [string]$BackendZip = "backend-deploy.zip",
    [string]$FrontendDir = "frontend"
)

$ErrorActionPreference = "Stop"

function Write-Stage {
    param([string]$Message)
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Assert-AwsCli {
    if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
        throw "AWS CLI is not installed or not on PATH. Install from https://aws.amazon.com/cli/ and run aws configure."
    }
}

function Prepare-BackendZip {
    param([string]$ZipPath)

    if (Test-Path $ZipPath) {
        Remove-Item $ZipPath -Force
    }

    Write-Stage "Packaging backend"
    $itemsToInclude = @("app", "main.py", "requirements.txt", ".ebextensions", "Procfile") | Where-Object { Test-Path $_ }
    if (-not $itemsToInclude) {
        throw "Required backend files (app/, main.py, requirements.txt, etc.) not found."
    }

    $pythonCode = @"
import os, sys, zipfile
items = ["app", "main.py", "requirements.txt", ".ebextensions", "Procfile"]
zip_path = sys.argv[1]
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for item in items:
        if not os.path.exists(item):
            continue
        if os.path.isdir(item):
            for root, _, files in os.walk(item):
                for file_name in files:
                    full_path = os.path.join(root, file_name)
                    arcname = os.path.relpath(full_path).replace(os.sep, "/")
                    zf.write(full_path, arcname)
        else:
            zf.write(item, item.replace(os.sep, "/"))
"@
    $pythonCode | python - $ZipPath
    Write-Host "Created package $ZipPath" -ForegroundColor Green
}

function Deploy-Backend {
    param(
        [string]$ZipPath,
        [string]$Region,
        [string]$EbApplicationName,
        [string]$EbEnvironmentName,
        [string]$EbDeploymentBucket
    )

    Write-Stage "Uploading backend bundle to S3 ($EbDeploymentBucket)"
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $s3Key = "$EbApplicationName/$timestamp.zip"

    aws s3 cp $ZipPath "s3://$EbDeploymentBucket/$s3Key" --region $Region | Out-Host

    Write-Stage "Creating EB application version"
    $versionLabel = "v-$timestamp"
    aws elasticbeanstalk create-application-version `
        --application-name $EbApplicationName `
        --version-label $versionLabel `
        --source-bundle S3Bucket=$EbDeploymentBucket,S3Key=$s3Key `
        --region $Region | Out-Host

    Write-Stage "Updating EB environment"
    aws elasticbeanstalk update-environment `
        --environment-name $EbEnvironmentName `
        --version-label $versionLabel `
        --region $Region | Out-Host

    Write-Host "Waiting for environment to update..." -ForegroundColor Yellow
    aws elasticbeanstalk wait environment-updated `
        --environment-name $EbEnvironmentName `
        --region $Region | Out-Host

    $envUrl = aws elasticbeanstalk describe-environments `
        --environment-names $EbEnvironmentName `
        --region $Region `
        --query "Environments[0].CNAME" `
        --output text
    Write-Host "Backend deployed: http://$envUrl" -ForegroundColor Green
}

function Build-Frontend {
    param([string]$FrontendDir)

    Write-Stage "Building frontend"
    Push-Location $FrontendDir
    try {
        if (Test-Path package-lock.json) {
            npm ci | Out-Host
        } else {
            npm install | Out-Host
        }
        npm run build | Out-Host
    }
    finally {
        Pop-Location
    }
}

function Deploy-Frontend {
    param([string]$FrontendDir, [string]$FrontendBucket, [string]$Region)

    $distPath = Join-Path $FrontendDir "dist"
    if (-not (Test-Path $distPath)) {
        throw "Frontend build output '$distPath' was not found. Run the build step first."
    }

    Write-Stage "Syncing frontend to S3 ($FrontendBucket)"
    aws s3 sync $distPath "s3://$FrontendBucket/" --delete --region $Region | Out-Host
}

function Invalidate-CloudFront {
    param([string]$DistributionId)

    Write-Stage "Invalidating CloudFront ($DistributionId)"
    aws cloudfront create-invalidation `
        --distribution-id $DistributionId `
        --paths "/*" | Out-Host
}

try {
    Assert-AwsCli
    Prepare-BackendZip -ZipPath $BackendZip
    Deploy-Backend -ZipPath $BackendZip -Region $Region -EbApplicationName $EbApplicationName -EbEnvironmentName $EbEnvironmentName -EbDeploymentBucket $EbDeploymentBucket
    Build-Frontend -FrontendDir $FrontendDir
    Deploy-Frontend -FrontendDir $FrontendDir -FrontendBucket $FrontendBucket -Region $Region
    Invalidate-CloudFront -DistributionId $CloudFrontDistributionId

    Write-Stage "Deployment complete"
    Write-Host "Check backend health at http://<EB CNAME>/health and verify the frontend after cache invalidation." -ForegroundColor Green
}
catch {
    Write-Error $_
    exit 1
}
finally {
    if (Test-Path $BackendZip) {
        Remove-Item $BackendZip -Force
    }
}
