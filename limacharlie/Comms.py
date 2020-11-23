from .utils import LcApiException
from .utils import GET
from .utils import DELETE
from .utils import POST
from .utils import HEAD
from .utils import PATCH

from .Manager import Manager
from .Manager import ROOT_URL

import uuid
import sys
import json

class Comms( object ):
    '''Representation of a limacharlie.io Comms.'''

    def __init__( self, manager ):
        self._manager = manager

    def createRoom( self, nickname = None ):
        '''Create a new Room.

        Args:
            nickname (str): optional nickname to give the new room.
        Returns:
            a Room object.
        '''
        req = {
            'oid': self._manager._oid,
        }
        if nickname is not None:
            req[ 'nickname' ] = str( nickname )
        data = self._manager._apiCall( 'comms/room', POST, req, altRoot = ROOT_URL )
        return Room( self._manager, data[ 'rid' ] )

    def getRoom( self, rid ):
        '''Initialize an existing Room object.

        Args:
            rid (str): room id of the Room to initialize.
        Returns:
            a Room object.
        '''
        return Room( self._manager, rid )

    def search( self, filters = {} ):
        '''Search for matching Rooms across all available Orgs.

        Args:
            filters (dict): dictionary of all the filter terms,
        Returns:
            A list of matching Rooms.
        '''
        filters = { k : v for k, v in filters.items() if v is not None }
        return self._manager._apiCall( 'comms/search', GET, queryParams = filters, altRoot = ROOT_URL )

class Room( object ):
    '''Representation of a limacharlie.io Comms Room.'''

    def __init__( self, manager, rid ):
        self._manager = manager
        try:
            uuid.UUID( rid )
        except:
            raise LcApiException( 'Invalid sid, should be in UUID format.' )
        self.rid = str( rid )

    def getOverview( self ):
        '''Get overview information about the Room.

        Returns:
            room overview dict.
        '''
        return self._manager._apiCall( 'comms/room/%s' % self.rid, HEAD, altRoot = ROOT_URL )

    def delete( self ):
        '''Delete a Room.'''
        return self._manager._apiCall( 'comms/room/%s' % self.rid, DELETE, altRoot = ROOT_URL )

    def getDetails( self ):
        '''Get detailed information about the Room.

        Returns:
            room details dict.
        '''
        return self._manager._apiCall( 'comms/room/%s' % self.rid, GET, altRoot = ROOT_URL )

    def merge( self, toMerge = [] ):
        '''Merge a set of Rooms into this Room.

        Args:
            toMerge (str list): list of room id to merge into this Room.
        '''
        req = {
            'rid': toMerge,
        }
        return self._manager._apiCall( 'comms/room/%s' % self.rid, PATCH, req, altRoot = ROOT_URL )

    def update( self, nickname = None, priority = None, status = None ):
        '''Update room information.

        Args:
            nickname (str): optional nickname to set.
            priority (int): optional priority to set.
            status (str): optional status to set.
        '''
        req = {}
        if nickname is not None:
            req[ 'nickname' ] = nickname
        if priority is not None:
            req[ 'priority' ] = int( priority )
        if status is not None:
            req[ 'status' ] = str( status )
        return self._manager._apiCall( 'comms/room/%s' % self.rid, POST, req, altRoot = ROOT_URL )

    def addLink( self, linkType, linkValue ):
        '''Add a link to a Room.

        Args:
            link (str): link to add.
        '''
        req = {
            'type' : linkType,
            'value' : linkValue,
        }
        return self._manager._apiCall( 'comms/room/%s/link' % self.rid, POST, req, altRoot = ROOT_URL )

    def removeLink( self, linkType, linkValue ):
        '''Remove a link from a Room.

        Args:
            link (str): link to remove.
        '''
        req = {
            'type' : linkType,
            'value' : linkValue,
        }
        return self._manager._apiCall( 'comms/room/%s/link' % self.rid, DELETE, req, altRoot = ROOT_URL )

def main( sourceArgs = None ):
    import argparse

    parser = argparse.ArgumentParser( prog = 'limacharlie comms' )
    subparsers = parser.add_subparsers( dest = 'object', help = 'object to work with' )

    objects = {
        'room' : subparsers.add_parser( 'room', help = 'working with rooms' ),
    }

    # room
    subparsers_room = objects[ 'room' ].add_subparsers( dest = 'action', help = 'action to take' )

    # room:create
    parser_room_create = subparsers_room.add_parser( 'create', help = 'create a room' )
    parser_room_create.add_argument( '--nickname', type = str, help = 'nickname of the room' )

    # room:get
    parser_room_get = subparsers_room.add_parser( 'get', help = 'get a room' )
    parser_room_get.add_argument( 'rid', type = str, help = 'room id' )

    # room:search
    parser_room_search = subparsers_room.add_parser( 'search', help = 'search for rooms' )
    parser_room_search.add_argument( '--oid', type = str, help = 'on search org oid' )
    parser_room_search.add_argument( '--cursor', type = str, help = 'search cursor' )
    parser_room_search.add_argument( '--assignee', type = str, help = 'has assignee' )
    parser_room_search.add_argument( '--last-change-before', type = str, help = 'last changed before' )
    parser_room_search.add_argument( '--last-change-after', type = str, help = 'last changed after' )
    parser_room_search.add_argument( '--created-by', type = str, help = 'created-by' )
    parser_room_search.add_argument( '--status', type = str, help = 'status' )
    parser_room_search.add_argument( '--priority-above', type = str, help = 'priority is above' )
    parser_room_search.add_argument( '--priority-below', type = str, help = 'priority is below' )
    parser_room_search.add_argument( '--link', type = str, nargs = '*', help = 'link' )

    # room:add_link
    parser_room_add_link = subparsers_room.add_parser( 'add-link', help = 'add a link to a room' )
    parser_room_add_link.add_argument( 'rid', type = str, help = 'room id' )
    parser_room_add_link.add_argument( 'linkType', type = str, help = 'link type' )
    parser_room_add_link.add_argument( 'linkValue', type = str, help = 'link value' )

    # room:remove_link
    parser_room_remove_link = subparsers_room.add_parser( 'remove-link', help = 'remove a link from a room' )
    parser_room_remove_link.add_argument( 'rid', type = str, help = 'room id' )
    parser_room_remove_link.add_argument( 'linkType', type = str, help = 'link value' )
    parser_room_remove_link.add_argument( 'linkValue', type = str, help = 'link value' )

    args = parser.parse_args( sourceArgs )

    if args.object is None:
        parser.print_help()
        sys.exit( 1 )
    if args.action is None:
        objects[ args.object ].print_help()
        sys.exit( 1 )

    def createRoom():
        return {
            'rid': Comms( Manager() ).createRoom( args.nickname ).rid,
        }

    def getRoom():
        return Comms( Manager() ).getRoom( args.rid ).getDetails()

    def searchRooms():
        return Comms( Manager() ).search( filters = vars( args ) )

    def addRoomLink():
        return Comms( Manager() ).getRoom( args.rid ).addLink( args.linkType, args.linkValue )

    def removeRoomLink():
        return Comms( Manager() ).getRoom( args.rid ).removeLink( args.linkType, args.linkValue )

    result = {
        'room:create' : createRoom,
        'room:get' : getRoom,
        'room:search' : searchRooms,
        'room:add-link' : addRoomLink,
        'room:remove-link' : removeRoomLink,
    }[ '%s:%s' % ( args.object, args.action ) ]()

    print( json.dumps( result, indent = 2 ) )

if __name__ == '__main__':
    main()