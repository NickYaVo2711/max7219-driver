from machine import Pin, SPI
from time import sleep
#cs = Erwin von Pinsten

class Display:
    animation = 0.1
    bufferlock = True
    buffer = [[0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0]]
    
    def __init__(self, block, clk, din, cs):
    #init speichert alle benötigten Pins für die weitere Nutzung ab
        
        self.block = block
        #block steht für den SPI Block, in dem die Pins liegen
        self.clk = clk
        self.din = din
        self.cs = Pin(cs, Pin.OUT)
        
    def startup(self):
    #startup setzt alle Register des Chips auf die für normalen Betrieb benötigten Werte
        
        self.spi =  SPI(self.block, baudrate=10000, sck=Pin(self.clk),mosi=Pin(self.din),miso=Pin(12), bits=8, firstbit=SPI.MSB)
        #initiiert die SPI Kommunikation mit dem Chip
        
        self.cs.off()
        self.spi.write(bytearray([0x09, 0x00]))
        self.cs.on()
        sleep(0.1)
        #schaltet den Decoder ab
        
        self.cs.off()
        self.spi.write(bytearray([0x0F, 0x00]))
        self.cs.on()
        sleep(0.1)
        #setzt das Test Register auf Normalbetrieb
        
        self.cs.off()
        self.spi.write(bytearray([0x0A, 0x01]))
        self.cs.on()
        sleep(0.1)
        #setzt die Helligkeit auf den niedrigsten Wert
        
        self.cs.off()
        self.spi.write(bytearray([0x0B, 0x07]))
        self.cs.on()
        sleep(0.1)
        #setzt das Scan Limit auf 7, d.h. alle Spalten werden dargestellt
        
        self.cs.off()
        self.spi.write(bytearray([0x0C, 0x01]))
        self.cs.on()
        sleep(0.1)
        #setzt das Shutdown Register auf Normalbetrieb
        
        for i in range(8):
            self.cs.off()
            self.spi.write(bytearray([int(hex(i+1)), 0x00]))
            self.cs.on()
            sleep(0.1)
        #leert das ganze Display -> geht jede Reihe durch und setzt sie mit 0x00 auf den Binärcode 00000000

    def setPixel(self, row, column, skip = None):
    #setPixel stellt einen Pixel einzeln dar, jedoch ist nur einer Pro Zeile gleichzeitig möglich
        if skip == None:
            skip = False
        if 0 < row < 9:
            if 0 < column < 9:
                if self.bufferlock == False:
                    self.buffer[row-1][column-1] = 1
                if skip == False:
                    self.cs.off()
                    column = 2**(abs(column-8))
                    self.spi.write(bytearray([int(hex(row)), int(hex(column))]))
                    self.cs.on()
                    """
                    Das Programm rechnet an diese Stelle die Hex-Zahl für den Binärcode aus, der eine Pixelreihe darstellt.
                    Jedoch nimmt die Funktion die Stelle des Pixels als Integer an. Um dies zu konvertieren, rechnet das
                    Programm die Basis des Binärsystems 2 hoch des Betrags der Stelle - 8 -> 2**(|PIXEL_STELLE-8|). Dies
                    ergibt den Binärcode, für den Pixel 3 wäre dieser 00100000. Dies wird in eine Hex Zahl umgewandelt
                    und per SPI an den Chip übertragen.
                    """
                sleep(self.animation)
            else:
                print('ERROR:invalid column input')
        else:
            print('ERROR:invalid row input')
        #überprüft, ob der Input im gültigen Zahlenbereich liegt und stellt den Pixel dar
            
    def setColumn(self, row, columns, skip = None):
    #setColumn stellt immer eine ganze Reihe dar
        if skip == None:
            skip = False
        column_data = 0
        for i in range(len(columns)):
            if columns[i] < 1:
                print('ERROR:invalid column input')
                return
            else: 
                if columns[i] > 8:
                    print('ERROR:invalid column input')
                    return
                else:
                    if self.bufferlock == False:
                        self.buffer[row-1][columns[i]-1] = 1
                        
                    column_data = column_data + 2**(abs(columns[i]-8))
                    """
                    Hier wird analog zu der Methode setPixel die Binärzahl errechnet,
                    hier jedoch in einer Schleife die das ganze Array mit den Pixelpositionen
                    einmal durchgeht und dabei auch prüft, ob der Input im gültigen Zahlenbereich liegt.
                    """
        if skip == False:
            self.cs.off()
            self.spi.write(bytearray([int(hex(row)), column_data]))
            self.cs.on()
        sleep(self.animation)
        #sendet die Positionen an den Chip
        
    def setBrightness(self, brightness):
    #ändert die Helligkeit der LEDs
        if 0 < brightness < 16:
            self.cs.off()
            self.spi.write(bytearray([0x0A, int(hex(brightness))]))
            #sendet die Helligkeit an den Chip
            self.cs.on()
        else:
            print('ERROR:invalid brightness setting')
        #überprüft, ob der Input im gültigen Zahlenbereich liegt und stellt die Helligkeit ein
    
    #setzt das delay zwischen der generierung von einzelnen reihen
    def setAnimation(self, animation):
        if animation == 'reset':
            self.animation = 0.1
        else:
            self.animation = animation
    
    def clearAll(self):
    #löscht das ganze Display
        for i in range(8):
            self.cs.off()
            self.spi.write(bytearray([int(hex(i+1)), 0x00]))
            self.cs.on()
            sleep(self.animation)
        #leert das ganze Display -> geht jede Reihe durch und setzt sie mit 0x00 auf den Binärcode 00000000
    
    #lädt einen Pixel in den Buffer
    def bufferPixel(self, row, column):
        self.setPixel(row, column, True)
    
    #lädt eine Zeile in den Buffer
    def bufferColumn(self, row, columns):
        self.setColumn(row, columns, True)
    
    #invertiert der buffer
    def invertBuffer(self):
        for i in range(8):
            for n in range(8):
                self.buffer[i][n] = abs(self.buffer[i][n] - 1)
    
    #leert den buffer
    def clearBuffer(self):
        for i in range(8):
            for n in range(8):
                self.buffer[i][n] = 0
    
    #entsperrt den buffer
    def startBuffer(self):
        self.bufferlock = False
        self.clearBuffer()
    
    #sperrt den buffer
    def stopBuffer(self):
        self.bufferlock = True
    
    #gibt den buffer in der kommandozeile aus
    def showBuffer(self):
        for i in range(8):
            print(self.buffer[i][:])
        print('\n')
    
    #schreibt den bufferinhalt aufs display
    def printBuffer(self):
        for i in range(9):
            self.cs.off()
            self.spi.write(bytearray([int(hex(i)), int("".join(str(n) for n in self.buffer[i-1][:]),2)]))
            self.cs.on()
            sleep(self.animation)
    
    def testAll(self):
    #führt einen Selbsttest durch
        for i in range(5):
            self.cs.off()
            self.spi.write(bytearray([0x0F, 0x01]))
            self.cs.on()
            sleep(0.5)
            self.cs.off()
            self.spi.write(bytearray([0x0F, 0x00]))
            self.cs.on()
            sleep(0.5)
        #setzt 5 mal das Testregister, wobei alle LEDs auf voller Helligkeit leuchten