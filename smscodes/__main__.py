from smscodes.app import app, init

if __name__ == '__main__':
    init()
    app.run('0.0.0.0', 8081)
