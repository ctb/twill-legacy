def test(*args):
    print 'function test passed %d args' % (len(args),)
    print 'args are:', args

print "---"
print "imported function 'test';"
print "try 'test hello world!'"
print "---"
