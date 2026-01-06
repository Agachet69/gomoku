NAME        := gomoku
VENV        := .venv
PY          := $(VENV)/bin/python
ENTRY       := srcs/gomoku.py

all: $(NAME)

$(NAME): $(VENV) requirements.txt
	@echo '#!/usr/bin/env bash' > $(NAME)
	@echo 'exec $(PY) $(ENTRY) "$$@"' >> $(NAME)
	@chmod +x $(NAME)

$(VENV):
	python3 -m venv $(VENV)
	$(PY) -m pip install -r requirements.txt

clean:
	rm -rf __pycache__ srcs/__pycache__

fclean: clean
	rm -rf $(VENV) $(NAME)

re: fclean all

run: $(NAME)
	@./$(NAME)

.PHONY: all clean fclean re run