# GringoOps Command Center

clean:
	./cleanup.sh

launch:
	python3 gringo_launcher.py

gui:
	python3 gui_launcher.py

agent:
	python3 agent_cli.py

tools:
	python3 tools/repair_engine.py && \
	python3 tools/openai_review.py && \
	python3 tools/gemini_query.py && \
	python3 tools/hf_runner.py

keys:
	python3 manage_keys.py

wizard:
	python3 wizard.py

dashboard:
	python3 gringoops_dashboard.py

rebuild:
	make clean && bash setup_agent.sh

firebase-deploy:
	firebase deploy

streamlit:
	streamlit run streamlit_app/app.py

scaffold:
	python3 run_scaffolder.py
