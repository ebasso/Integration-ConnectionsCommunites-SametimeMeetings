import getpass, base64

#senha = raw_input('Password:')
senha = getpass.getpass()

encoded = base64.b64encode(senha)
print 'encoded => "%s"' % encoded

#decoded = base64.b64decode(encoded)
#print 'decoded => "%s"' % decoded
