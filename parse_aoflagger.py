#!/usr/bin/env python
"""
Script that reads the output from an NDPPP AOFlagger run and outputs the flags as numpy arrays.

Author: P. Salas (Leiden Observatory)
"""

import sys
import logging
import argparse

import numpy as np

def parse_args():
    """
    Parse the command line arguments.
    """
    
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('filein', type=str,
                        help="File with the output from AOFlagger.\n" \
                             "E.g., aoflag.log (string).\n")
    parser.add_argument('output', type=str,
                        help="Basename for the arrays with the flags.\n" \
                             "E.g., aoflag_out (string).\n")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Verbose output?")
    parser.add_argument('-l', '--logfile', type=str, default=None,
                        help="Where to store the logs.\n" \
                             "(string, Default: output to console)")
    args = parser.parse_args()
    
    return args

def parse_flags(filein, logger):
    """
    """
    
    logger.info('Will read file {0} parsing the flags'.format(filein))

    read = False
    
    with open(filein, 'r') as log:
        for line in log:
            
            if line.startswith('Total flagged:'):
                read = False
            
            if ' nchan:' in line:
                nchan = int(line.split(' ')[-3])
                logger.info('Number of channels: {0}'.format(nchan))
                chflags = np.zeros(nchan)
                
            if read and not line.startswith(' channels'):
                #print line.rstrip().split()
                chindx = line.index(':')
                chrng = ''.join(line.rstrip()[:chindx].split())
                #print 'chrng: ', chrng
                ch0 = int(chrng.split('-')[0])
                chf = int(chrng.split('-')[-1])
                #print line.rstrip()[chindx+1:].split()
                logger.debug('Reading flags for channel range {0}--{1}'.format(ch0, chf))
                flags = [s.strip('%') for s in line.rstrip()[chindx+1:].split()]
                #print flags
                chflags[ch0:chf+1] = flags # [s.strip('%') for s in line.rstrip()[chindx:].split()]
            
            if line.startswith('Percentage of visibilities flagged per channel:'):
                logger.debug('Will start reading the flags per channel.')
                
                read = True
                
                logger.debug(line)
                
    return chflags        

def make_logger(verbose, logfile):
    """
    """
    
    if verbose:
        loglev = logging.DEBUG
    else:
        loglev = logging.ERROR
        
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=logfile, level=loglev, format=formatter)
    
    logger = logging.getLogger(__name__)
    
    return logger

if __name__ == '__main__':
    
    # Parse the command line arguments
    args = parse_args()
    
    # Create a logger
    logger = make_logger(args.verbose, args.logfile)

    # Start parsing
    chflags = parse_flags(args.filein, logger)
    
    np.save(args.output+'_chflags.npy', chflags)