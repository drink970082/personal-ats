APP_NAME=ats-app
DB_FILE=applications.db
PORT=8050

build:
	docker build -t $(APP_NAME) .

save:
	docker save -o $(APP_NAME).tar $(APP_NAME)

run-new:
	docker run -p $(PORT):8050 $(APP_NAME)

run-persist:
	docker run -p $(PORT):8050 -v $(PWD)/$(DB_FILE):/app/$(DB_FILE) $(APP_NAME)

copy-db:
	@echo "Find your running container ID with: docker ps"
	@read -p "Enter container ID: " cid; \
	docker cp $$cid:/app/$(DB_FILE) .

clean-db:
	rm -f $(DB_FILE)

make-dummy-data:
	python generate_dummy_data.py