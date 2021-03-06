import cgi
from http.server import BaseHTTPRequestHandler,HTTPServer

from db_setup import Base,Restaurant,MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurant"):
                self.send_response(200)
                self.send_header('content-type','text/html')
                self.end_headers()

                output=""
                output +='<html><body><h1><a href="/restaurant/new">Create a new Restaurant</a></h2>'
                output +='<h2>Restaurants List</h2>'
                listOfRes = session.query(Restaurant).all()
                for restaurant in listOfRes:
                    output+='<h3>%s</h3>' %(restaurant.name)
                    output+= '<br>'
                    editLink = "/restaurant/%s/edit" %(restaurant.id)
                    output+= '<a href="%s">Edit</a>' %(editLink)
                    output+='<br>'
                    deleteLink = "/restaurant/%s/delete" % restaurant.id
                    output+='<a href="%s">Delete</a>' % deleteLink
                output += "</body></html>"

                self.wfile.write(bytes(output,"UTF-8"))

                return
            if self.path.endswith("/delete"):
                restaurantId=self.path.split("/")[2]
                getResById = session.query(Restaurant).filter_by(id=restaurantId).one()
                if(getResById != []):
                    self.send_response(200)
                    self.send_header('content-type', 'text/html')
                    self.end_headers()

                    output = ""
                    output += "<html><body>"
                    output += "<h2>Do you want to delete this Restaurant?</h2>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurant/%s/delete'>" \
                                "<input type='submit' value='Delete'></form>" % restaurantId

                    output += "</body></html>"

                    self.wfile.write(bytes(output,"utf-8"))
                    return
            if self.path.endswith("/edit"):

                restaurantId=self.path.split("/")[2]
                getNameById = session.query(Restaurant).filter_by(id=restaurantId).one()
                if(getNameById != []):
                    self.send_response(200)
                    self.send_header('content-type', 'text/html')
                    self.end_headers()

                    output=""
                    output+="<html><body>"
                    output+="<h2>%s</h2>" %(getNameById.name)
                    output+= "<form method='POST' enctype='multipart/form-data' action='/restaurant/%s/edit'>" \
                              "<input name='editedName' placeholder='Enter New Name' type='text'>" \
                              "<input type='submit' value='Rename'></form>" %(restaurantId)
                    output+="</body></html>"
                    self.wfile.write(bytes(output,"utf-8"))
                    return

            if self.path.endswith("/restaurant/new"):
                self.send_response(200)
                self.send_header('content-type','text/html')
                self.end_headers()

                output=""
                output += '<html><body>'
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurant/new'><h1>Make a New Restaurant</h1>" \
                          "<input name='nameOfRes' type='text'><input type='submit' value='Create'></form>"
                output += "</body></html>"

                self.wfile.write(bytes(output,"UTF-8"))
                return
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('content-type','text/html')
                self.end_headers()

                output=""
                output=output+'<html><body><h1>Hello!</h1></body></html>'
                output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>what would like me to say?</h2>" \
                          "<input name='message' type='text'><input type='submit' value='Submit'></form>"
                output += "</body></html>"

                self.wfile.write(bytes(output,"UTF-8"))
                print(output)
                return

        except IOError:
            self.send_error(404,"FILE NOT FOUND %s" % self.path)
    def do_POST(self):
        try:
            if self.path.endswith("/delete"):
                restaurantId = self.path.split("/")[2]

                deleteRes = session.query(Restaurant).filter_by(id=restaurantId).one()
                if(deleteRes != []):
                    session.delete(deleteRes)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurant')
                    self.end_headers()
                return
            if self.path.endswith("/edit") :
                restaurantId = self.path.split("/")[2]
                ctype,pdict = cgi.parse_header(self.headers.get('content-type'))
                pdict['boundary'] = bytes(pdict['boundary'],"utf-8")
                fields=""
                if(ctype=='multipart/form-data'):
                    fields = cgi.parse_multipart(self.rfile,pdict)
                newName = fields.get('editedName')
                newName = newName[0].decode("utf-8")
                rename = session.query(Restaurant).filter_by(id=restaurantId).one()
                if rename != []:
                    rename.name = newName
                    session.add(rename)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurant')
                    self.end_headers()

            if(self.path.endswith("/restaurant/new")):
                ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
                pdict['boundary'] = bytes(pdict['boundary'], "UTF-8")
                if (ctype == 'multipart/form-data'):
                    fields = cgi.parse_multipart(self.rfile, pdict)
                nameOfRes = fields.get('nameOfRes')

                ResToDb = Restaurant(name=nameOfRes[0].decode("utf-8"))
                session.add(ResToDb)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location','/restaurant')
                self.end_headers()

            print("Output OK")

            return
        # output += "<h2>Okay,how about this:</h2>"
        # output += "<h1>"
        # self.wfile.write(bytes(output,"utf-8"))
        # self.wfile.write(nameOfRes[0])
        # output += ""
        # output +=" </h1>"
        # output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2>
        # 			<input name="message" type="text" ><input type="submit" value="Submit"> </form>'''

        except:
            pass
def main():
    try:
        port = 8080
        server = HTTPServer(('',port),webserverHandler)
        print(("web server running on port %s" % port))
        server.serve_forever()

    except KeyboardInterrupt:
        print("^C entered, stopping web server...")
        server.socket.close()

if __name__=='__main__':
    main()