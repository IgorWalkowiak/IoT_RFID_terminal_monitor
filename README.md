1. Wymagania projektowe
	1.1. System umożliwia kontrolę użyć dowolnego sprzętu posiadający unikalny identyfikator w szczególności został opracowany dla technologii RFID. Rejestruje czas odbicia, na tej podstawie oblicza czas (np. przebywania w pomieszczeniu lub pracy) i generuje raporty w formacie csv. System zapewnia bezpieczeństwo poprzez TLS jak i zarządzanie ruchem przez brokera Mosquitto.

	1.2. Wymagania niefunkcjonalne:
* Python3
* OpenSSL
* Mosquitto
* Linux lub Windows10

2. Opis architektury systemu
System został zrealizowany w architekturze serwer – klient. Klientem są komputery(np Raspberry pi) z modułem odczytu kart RFID. Komunikują się one z brokerem Mosquitto który zapewnia im dostęp do komunikatów z i do serwera. Serwer to komputer który kontroluje ruch użytkowników, posiada bazę danych z użytkownikami i konfiguracją. 

3. Opis implementacji i zastosowanych rozwiązań
* Podana implementacja mockuje odczyt kart RFID w funkcji  closeUpCheckerLoop() - funkcja ta wykonywana jest w pętli. Docelowe rozwiązanie powinno implementować odczyt w tej właśnie funkcji, gdzie zawiadomienie o odczycie numeru karty RFID odbywa się przez wywołanie funkcji callAboutCloseUp(card_id) gdzie card_id to numer karty.
* Implementacja i subskrybcja MQTT odbywa się w funkcjach init. Dodatkowo oba programy – serwer i klient – posiadają globalnego klienta MQTT.

Client.py:
	def init():
 	   client.tls_set("ca.crt")
	    client.username_pw_set(username='client', password=mqttPassword)
	    client.connect(broker,port)
	    client.on_message = onMessage
	    client.loop_start()
	    client.subscribe("server/ack")

Klient subskrybuje się jedynie na wiadomość „server/ack” używaną do kontroli połączenia. MqttPassword to hasło do użytkownika client dodane w 6.1.3 jako [hasło_client].

Server.py:
	def init():
	    client.tls_set("ca.crt")
	    client.username_pw_set(username='server', password=mqttPassword)
	    client.connect(broker,port)
	    client.on_message = onMessage
	    client.loop_start()
	    client.subscribe("terminal/closeup")
	    client.subscribe("terminal/register")

Serwer subskrybuje się na wiadomości „terminal/closeup” używaną do informowania przez klientów o nowym zbliżeniu karty i na wiadmość „terminal/register” używaną do informowania przez klientów o podłączeniu się nowego terminala. MqttPassword to hasło do użytkownika server dodane w 6.1.3 jako [hasło_serwera].

Broker to zmienna odpowiadająca za nazwę domeny/ip brokera mosquitto, a zmienna port to port brokera mosquitto.

Certyfikat ca.crt to certyfikat wymagany do skonfigurowania połączenia TLS.

* Serwer posiada stworzoną na własne potrzeby bazę danych której interfejs wygląda następująco:
- getUserWithCardId(cardId)
- getUserWithName(name)
- addNewUser(user)
- removeUserByName(name)
- getTerminalWithId(terminalId)
- addNewTerminal(terminal)
- removeTerminalById(terminalId)
- logDoorUsage(time, cardId, terminalId)
- logForbiddenAttempt(time, cardId, terminalId)
- getUserHistory(user)
* System przechowuje informacji o terminalach i kartach w formacie .json – umożliwia to łatwe sprzężenie z innymi systemami ze względu na prosty i czytelny format.

4. Opis działania i prezentacja interfejsu
	4.1. Konfiguracja brokera Mosquitto:	
		4.1.1. Pobierz i zainstaluj brokera Mosquitto z https://mosquitto.org/download.
		4.1.2. Domyślnie broker działa na porcie 1883, jeśli potrzebujesz go zmienić dodaj do pliku mosquitto.conf (w folderze z zainstalowanym brokerem) linie:
			port [numer_portu]
		4.1.3. Za pomocą linii poleceń dodaj użytkowników z hasłami w podany sposób:
			mosquitto_passwd -b [ścieżka_do_pliku_z_hasłami] client [hasło_klienta]
			mosquitto_passwd -b [ścieżka_do_pliku_z_hasłami] server [hasło_serwera]
		6.1.4. Dodaj plik kontroli dostępu w [ścieżka_do_pliku_z_kontrolą_dostępu] i dodaj następujące uprawnienia:
			user server
			topic read terminal/closeup
			topic read terminal/register
			topic server/ack
			user client
			topic terminal/closeup
			topic terminal/register
			topic read server/ack
		4.1.5. Dodaj do pliku mosquitto.conf (w folderze z zainstalowanym brokerem) linie:
			broker = [nazwa_domeny_serwera_z_brokerem]
			allow_anonymous false
			password_file [ścieżka_do_pliku_z_hasłami]
			acl_file [ścieżka_do_pliku_z_kontrolą_dostępu]

	4.2 Wygeneruj certyfikaty TLS:
		4.2.1 Za pomoc linii poleceń zrób kolejno:
		* klucze dla certyfikatu poprzez:
			openssl genrsa -des3 -out ca.key 2048
		* certfikat za pomocą klucza utworzonego wcześniej poprzez:
			openssl req -new -x509 -days 1826 -key ca.key -out ca.crt
		* klucze dla brokera poprzez
			openssl genrsa -out server.key 2048
		* żądanie podpisania certyfikatu. (Pole Common Name musi być wypełnione nazwą domeny serwera brokera)
			openssl req -new -out server.csr -key server.key
		4.2.2 Skopiuj pliki ca.crt, servert.crt i server.key do stworzonego folderu w [ścieżka_do_folderu_z_certyfikatami].
		4.2.3 Dodaj do pliku mosquitto.conf który jest w folderze z zainstalowanym Mosquitto
			cafile [ścieżka_do_folderu_z_certyfikatami]\ca.crt
			certfile [ścieżka_do_folderu_z_certyfikatami]\server.crt
			keyfile [ścieżka_do_folderu_z_certyfikatami]\server.key

5. Literatura
- https://mosquitto.org/
- https://www.openssl.org/docs/
