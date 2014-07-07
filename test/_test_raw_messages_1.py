import os
import sys
import unittest

os.environ['DEBUG'] = "1"
if os.path.realpath( '../' ) not in sys.path:
    sys.path.insert( 0, os.path.realpath( '../' ) )

if os.path.realpath( '.' ) not in sys.path:
    sys.path.insert( 0, os.path.realpath( '.' ) )

from pyorient.utils import *
from pyorient.Messages.Constants.OrientPrimitives import *
from pyorient.Messages.ConnectMessage import ConnectMessage
from pyorient.Messages.DbExistsMessage import DbExistsMessage
from pyorient.Messages.DbOpenMessage import DbOpenMessage
from pyorient.Messages.DbCreateMessage import DbCreateMessage
from pyorient.Messages.DbDropMessage import DbDropMessage
from pyorient.OrientSocket import OrientSocket
from pyorient.OrientException import *


class CommandTestCase(unittest.TestCase):
    """ Command Test Case """

    def test_not_singleton_socket(self):
        connection = OrientSocket( "localhost", int( 2424 ) )
        connection2 = OrientSocket( "localhost", int( 2424 ) )
        assert id(connection.get_connection()) != id(connection2.get_connection())

    def test_connection(self):
        connection = OrientSocket( "localhost", int( 2424 ) )
        msg = ConnectMessage( connection )
        print "%r" % msg.get_protocol()
        assert msg.get_protocol() != -1

        session_id = msg.prepare( ("admin", "admin") )\
            .send_message().fetch_response()
        """
        alternative use
            session_id = msg.set_user("admin").set_pass("admin").prepare()\
            .send_message().fetch_response()
        """

        assert session_id == connection.session_id
        assert session_id != -1

        msg.close()
        print "%r" % msg._header
        print "%r" % session_id

    def test_db_exists(self):

        connection = OrientSocket( "localhost", int( 2424 ) )
        msg = ConnectMessage( connection )
        print "%r" % msg.get_protocol()
        assert msg.get_protocol() != -1

        session_id = msg.prepare( ("admin", "admin") )\
            .send_message().fetch_response()

        print "Sid: %s" % session_id
        assert session_id == connection.session_id
        assert session_id != -1

        db_name = "GratefulDeadConcerts"
        # params = ( db_name, STORAGE_TYPE_MEMORY )
        params = ( db_name, STORAGE_TYPE_LOCAL )

        msg = DbExistsMessage( connection )

        exists = msg.prepare( params ).send_message().fetch_response()
        assert exists is True

        msg.close()
        print "%r" % exists

    def test_db_open_connected(self):

        connection = OrientSocket( "localhost", int( 2424 ) )
        conn_msg = ConnectMessage( connection )

        print "%r" % conn_msg.get_protocol()
        assert conn_msg.get_protocol() != -1

        session_id = conn_msg.prepare( ("admin", "admin") )\
            .send_message().fetch_response()

        print "Sid: %s" % session_id
        assert session_id == connection.session_id
        assert session_id != -1
        # ##################

        msg = DbOpenMessage( connection )

        db_name = "GratefulDeadConcerts"
        cluster_info = msg.prepare(
            ("admin", "admin", "", db_name, DB_TYPE_DOCUMENT)
        ).send_message().fetch_response()

        print "Cluster: %s" % cluster_info
        assert len(cluster_info) != 0

    def test_db_open_not_connected(self):

        connection = OrientSocket( "localhost", int( 2424 ) )

        print "Sid, should be -1 : %s" % connection.session_id
        assert connection.session_id == -1

        # ##################

        msg = DbOpenMessage( connection )

        db_name = "GratefulDeadConcerts"
        cluster_info = msg.prepare(
            ("admin", "admin", "", db_name, DB_TYPE_DOCUMENT)
        ).send_message().fetch_response()

        print "Cluster: %s" % cluster_info
        assert len(cluster_info) != 0

    def test_db_create_without_connect(self):

        connection = OrientSocket( "localhost", int( 2424 ) )

        try:
            ( DbCreateMessage( connection ) ).prepare(
                ("db_test", DB_TYPE_DOCUMENT, STORAGE_TYPE_LOCAL)
            ).send_message().fetch_response()

            assert True
            # exit(1)  # this should not happen if you have database
        except PyOrientConnectionException, e:
            assert True
            print e.message

    def test_db_create_with_connect(self):

        connection = OrientSocket( "localhost", int( 2424 ) )
        conn_msg = ConnectMessage( connection )
        print "Protocol: %r" % conn_msg.get_protocol()

        session_id = conn_msg.prepare( ("admin", "admin") )\
            .send_message().fetch_response()

        print "Sid: %s" % session_id
        assert session_id == connection.session_id
        assert session_id != -1

        # ##################

        db_name = "my_little_test"
        response = ''
        try:
            ( DbCreateMessage( connection ) ).prepare(
                (db_name, DB_TYPE_DOCUMENT, STORAGE_TYPE_LOCAL)
            ).send_message().fetch_response()
            assert False
            # exit(1)  # this should not happen if you have database
        except PyOrientCommandException, e:
            assert True
            print e.message

        print "Creation: %r" % response
        assert len(response) is 0

        msg = DbExistsMessage( connection )

        msg.prepare( (db_name, STORAGE_TYPE_LOCAL) )
        # msg.prepare( [db_name] )
        exists = msg.send_message().fetch_response()
        assert exists is True

        msg.close()
        print "%r" % exists

    def test_db_drop_without_connect(self):
        connection = OrientSocket( "localhost", int( 2424 ) )
        try:
            ( DbDropMessage( connection ) ).prepare(["test"]) \
                .send_message().fetch_response()

            #expected Exception
            assert False
            # exit(1)  # this should not happen if you have database
        except PyOrientConnectionException, e:
            assert True
            print e.message

    def test_db_create_with_drop(self):

        connection = OrientSocket( "localhost", int( 2424 ) )
        conn_msg = ConnectMessage( connection )
        print "Protocol: %r" % conn_msg.get_protocol()
        assert connection.protocol != -1

        session_id = conn_msg.prepare( ("admin", "admin") ) \
            .send_message().fetch_response()

        print "Sid: %s" % session_id
        assert session_id == connection.session_id
        assert session_id != -1

        # ##################

        db_name = "my_little_test"

        msg = DbExistsMessage( connection )
        exists = msg.prepare( [db_name] ).send_message().fetch_response()

        print "Before %r" % exists

        assert exists is True  # should happen every time because of latest test
        if exists is True:
            ( DbDropMessage( connection ) ).prepare([db_name]) \
                .send_message().fetch_response()

        print "Creation again"
        try:
            ( DbCreateMessage( connection ) ).prepare(
                (db_name, DB_TYPE_DOCUMENT, STORAGE_TYPE_LOCAL)
            ).send_message().fetch_response()
            assert True
        except PyOrientCommandException, e:
            print e.message
            assert False  # No expected Exception

        msg = DbExistsMessage( connection )
        exists = msg.prepare( [db_name] ).send_message().fetch_response()
        assert  exists is True

        msg.close()
        print "After %r" % exists



# test_not_singleton_socket()
# test_connection()
# test_db_exists()
# test_db_open_connected()
# test_db_open_not_connected()
# test_db_create_without_connect()
# test_db_create_with_connect()
# test_db_drop_without_connect()
# test_db_create_with_drop()