from twill import log


def test(*args):
    log.info('function test passed %d args', len(args))
    log.info('args are: %s', args)


log.info("---")
log.info("imported function 'test';")
log.info("try 'test hello world!'")
log.info("---")
