import datetime
import socket
import time
from beautifulsoup4 import BeautifulSoup

#Return the current time
def  get_time():
    return time.strftime("%H:%M:%S")

# flask server on port 3000 that returns the current time
def test_one():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 3000))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)
        if not data:
            break
        print(data)
        conn.send(get_time().encode())
        conn.close()




#method returning the opening times of a restaurant from google search
def get_opening_times(restaurant):
    #get the html from the google search
    url = "https://www.google.com/search?q=" + restaurant + " opening times"
    html = request.get(url).text
    #find the opening times in the html
    soup = BeautifulSoup(html, 'html.parser')
    times = soup.find_all("div", class_="dbg0pd")
    #return the opening times
    return times[0].text

    




get_opening_times('Rauner Linz')





    



