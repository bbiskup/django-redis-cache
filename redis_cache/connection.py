from redis.connection import UnixDomainSocketConnection, Connection


class CacheConnectionPool(object):

    def __init__(self):
        self._clients = {}
        self._connection_pools = {}

    def __contains__(self, server):
        return server in self._clients

    def __getitem__(self, server):
        return self._clients.get(server, None)

    def reset(self):
        for pool in self._connection_pools.itervalues():
            pool.disconnect()
        self._clients = {}
        self._connection_pools = {}

    def get_connection_pool(
        self,
        client,
        host='127.0.0.1',
        port=6379,
        db=1,
        password=None,
        parser_class=None,
        unix_socket_path=None,
        connection_pool_class=None,
        connection_pool_class_kwargs=None,
        **kwargs
    ):
        connection_identifier = (host, port, db, unix_socket_path)

        self._clients[connection_identifier] = client

        pool = self._connection_pools.get(connection_identifier)

        if pool is None:
            connection_class = (
                unix_socket_path and UnixDomainSocketConnection or Connection
            )

            kwargs = {
                'db': db,
                'password': password,
                'connection_class': connection_class,
                'parser_class': parser_class,
            }
            kwargs.update(connection_pool_class_kwargs)

            if unix_socket_path is None:
                kwargs.update({
                    'host': host,
                    'port': port,
                })
            else:
                kwargs['path'] = unix_socket_path

            pool = connection_pool_class(**kwargs)

            self._connection_pools[connection_identifier] = pool
            pool.connection_identifier = connection_identifier

        return pool

pool = CacheConnectionPool()
