test:
	@pre-commit run --all-files

run:
	@python3 -m WebStreamer

clean:
	@pyclean .

doppler:
	@doppler run -- python3 -m WebStreamer
