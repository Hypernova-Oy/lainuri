# Encrypting the vendor SDK, Docs, and Driver to prevent leaking confidential information to version control.

unarchive:
	echo "Unarchiving documents"
	gpg --batch --no-tty --yes --passphrase-file ../installer_secret_passphrase --decrypt -o documents.tar.gz documents.tar.gz.gpg
	tar -xzf documents.tar.gz

archive:
	echo "Archiving and encrypting all files in this directory"
	tar -czf documents.tar.gz --exclude='*.gpg' --exclude='*.tar.gz' *
	gpg --batch --no-tty --yes --passphrase-file ../installer_secret_passphrase --symmetric -o documents.tar.gz.gpg documents.tar.gz

