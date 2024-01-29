# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Automated release workflow with version bumping
- Conventional changelog generation
- Multi-architecture Docker builds (linux/amd64, linux/arm64)
- GitHub Container Registry (GHCR) publishing
- Comprehensive CI/CD pipeline with GitHub Actions
- Local testing scripts and troubleshooting guides

### Changed
- Updated to Kong 3.9.1 compatibility
- Modernized Kong API usage (replaced deprecated `ngx.ctx.authenticated_credential`)
- Enhanced Docker build process with proper dependency management
- Improved test coverage and mocking

### Fixed
- Docker build issues with long RUN commands
- Missing C compilation headers for lua-cjson
- Architecture-specific Docker image pulling
- Lua dependency management and testing

## [1.5.0-0] - 2024-01-XX

### Added
- Kong 3.9.x compatibility
- Support for `lua-resty-session ~> 4.0.5`
- Enhanced Docker image with multi-architecture support
- Comprehensive CI/CD pipeline

### Changed
- Updated Kong API usage for 3.x compatibility
- Modernized Docker build process
- Enhanced documentation and troubleshooting guides

### Fixed
- Docker build and dependency issues
- Architecture-specific image compatibility
- Lua module loading and testing

## [1.4.0-2] - Previous Release

### Added
- Initial Kong OIDC plugin implementation
- Basic OpenID Connect functionality
- Session management support

### Changed
- Kong 2.x compatibility
- Basic Docker support

### Fixed
- Various bug fixes and improvements
