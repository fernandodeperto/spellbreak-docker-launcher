import environ


@environ.config(prefix="SB")
class Config:
    @environ.config
    class Game:
        mode = environ.var("Solo")
        log_file = environ.var("server.log")

    @environ.config
    class Server:
        port = environ.var(7777, converter=int)
        idle_timer = environ.var(1800, converter=int)
        log_level = environ.var("INFO")

    game = environ.group(Game)
    server = environ.group(Server)


config = environ.to_config(Config)
