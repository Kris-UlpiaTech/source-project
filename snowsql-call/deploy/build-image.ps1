# Define variables
$dockerUser = "krizzon"
$imageName = "snowsql-call"
$tag = "latest"

# Log in to Docker Hub
Write-Host "Logging in to Docker Hub..."
docker login
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker login failed"
    exit 1
}

# Build the Docker image using the Dockerfile from the parent directory
# and set the build context to the parent folder (..)
Write-Host "Building the Docker image..."
docker build -f "../Dockerfile" -t "${dockerUser}/${imageName}:${tag}" ..
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed"
    exit 1
}

# Push the Docker image to Docker Hub
Write-Host "Pushing the Docker image to Docker Hub..."
docker push "${dockerUser}/${imageName}:${tag}"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker push failed"
    exit 1
}

Write-Host "✅ Build and push completed successfully!"
