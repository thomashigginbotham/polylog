# Polylog Makefile
# Common development tasks

.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*##"; printf "\033[36m\033[0m"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

.PHONY: install
install: install-backend install-frontend ## Install all dependencies

.PHONY: install-backend
install-backend: ## Install backend dependencies
	cd backend && poetry install || pip install -r requirements.txt

.PHONY: install-frontend
install-frontend: ## Install frontend dependencies
	cd frontend && npm install

.PHONY: dev
dev: ## Start development servers
	docker-compose up -d mongodb redis
	@echo "Starting backend and frontend in parallel..."
	@make -j2 dev-backend dev-frontend

.PHONY: dev-backend
dev-backend: ## Start backend development server
	cd backend && uvicorn app.main:app --reload --port 8000

.PHONY: dev-frontend
dev-frontend: ## Start frontend development server
	cd frontend && npm run dev

.PHONY: format
format: format-backend format-frontend ## Format all code

.PHONY: format-backend
format-backend: ## Format backend code
	cd backend && black . && isort .

.PHONY: format-frontend
format-frontend: ## Format frontend code
	cd frontend && npm run format

.PHONY: lint
lint: lint-backend lint-frontend ## Lint all code

.PHONY: lint-backend
lint-backend: ## Lint backend code
	cd backend && flake8 . && mypy .

.PHONY: lint-frontend
lint-frontend: ## Lint frontend code
	cd frontend && npm run lint

##@ Testing

.PHONY: test
test: test-backend test-frontend ## Run all tests

.PHONY: test-backend
test-backend: ## Run backend tests
	cd backend && pytest

.PHONY: test-frontend
test-frontend: ## Run frontend tests
	cd frontend && npm run test

.PHONY: test-coverage
test-coverage: ## Run tests with coverage
	cd backend && pytest --cov=app --cov-report=html
	cd frontend && npm run test:coverage

##@ Docker

.PHONY: docker-up
docker-up: ## Start all services with Docker Compose
	docker-compose up -d

.PHONY: docker-down
docker-down: ## Stop all Docker services
	docker-compose down

.PHONY: docker-build
docker-build: ## Build Docker images
	docker-compose build

.PHONY: docker-logs
docker-logs: ## Show Docker logs
	docker-compose logs -f

.PHONY: docker-clean
docker-clean: ## Clean Docker resources
	docker-compose down -v
	docker system prune -f

##@ Database

.PHONY: db-shell
db-shell: ## Open MongoDB shell
	docker exec -it polylog-mongodb mongosh

.PHONY: redis-cli
redis-cli: ## Open Redis CLI
	docker exec -it polylog-redis redis-cli

##@ Utilities

.PHONY: clean
clean: ## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true

.PHONY: setup
setup: ## Initial project setup
	cp frontend/.env.example frontend/.env
	cp backend/.env.example backend/.env
	@echo "Environment files created. Please edit them with your configuration."
	@echo "Run 'make install' to install dependencies."

.PHONY: check
check: lint test ## Run all checks (lint + test)

.PHONY: docs
docs: ## Generate documentation
	cd backend && python -m pdoc --html --output-dir docs app
	@echo "Backend documentation generated in backend/docs/"

.PHONY: api-docs
api-docs: ## Open API documentation in browser
	@echo "Opening API documentation..."
	@python -m webbrowser http://localhost:8000/docs
