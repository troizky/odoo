# -*- coding: utf-8 -*-

### Package wrapping ###

STX                 = '\x02' # Start byte
ETX                 = '\x03' # End byte
FS                  = '\x1c' # Parameteres separator
PASSWORD            = 'PIRI' # Password
PCKG_NAME           = '8'    # Package name byte # TODO shouldn't be a constant

### Commands of data receiving ###

FSCL_REQ            = '01'   # Fiscal shift counters and registers request
INFO_REQ            = '02'   # Information request
RCPT_REQ            = '03'   # Receipt data request
DEV_STATE_REQ       = '04'   # Printing device state request
STATUS_2_REQ        = '05'   # "Status 2" flags request

### Commands of setting parameters ###

WORK_START          = '10'   # Beginning of work
ST_READ             = '11'   # Settings table reading
ST_WRITE            = '12'   # Settings table writing
DT_READ             = '13'   # Date/time reading
DT_WRITE            = '14'   # Date/time writing
UPLOAD_LOGO         = '17'   # Upload logo
PRINT_LOGO          = '18'   # Print logo

### Commands of basic operations ###

X_REPORT            = '20'   # Print report without closing (X-report)
Z_REPORT            = '21'   # Print report with closing a shift (Z-report)
OPEN_DOC            = '30'   # Open a document
CLOSE_DOC           = '31'   # Complete the document
CANCEL_DOC          = '32'   # Cancel the document
PRINT_TEXT          = '40'   # Print a text
PRINT_BARCODE       = '41'   # Print a barcode # params: 0..3; 2..4; 1..255; 0..9?; barcode;
ADD_ITEM            = '42'   # Add an item into the receipt
DEL_ITEM            = '43'   # Remove the item from the receipt
SUB_TOTAL           = '44'   # Subtotal
ADD_PAYMENT         = '47'   # Payment
CASH_IN_OUT         = '48'   # Cash-in/Cash-out
COMPARE_TO_RCPT     = '52'   # Compare an amount to the receipt total
RCPT_COPY           = '53'   # Open a receipt copy
SHIFT_START         = '54'   # Open a new shift (shift=fiscal day)
PRINT_QR_CODE       = '55'   # Print a QR-code

### Commands for work with FM ###

EMERGENCY_CLOSE     = '63'   # Emergency close of the FA archive

### System commands ###

AUTH                = '90'   # Authorization
SET_BAUD_RATE       = '93'   # Set baud rate
TECH_RESET          = 'A2'   # Technical "zeroing" (Technological reset)
DATA_DUMP_REQ       = 'A3'   # Data dump request
DATA_DUMP_RECV      = 'A4'   # Data dump receiving
MF_STATE_RESET      = 'A5'   # The MF state reset
FA_STATUS_REQ       = 'B0'   # The FA status request
SHIFT_PARAMS_REQ    = 'B1'   # The current shift parameters request
FDO_EX_PARAMS_REQ   = 'B2'   # The FDO information exchange parameters request
INIT_FISCALIZATION  = 'B3'   # Initial fiscalization of the MF
RE_REGISTRATION     = 'B4'   # Re-registration of the MF
FISCAL_MODE_CLOSE   = 'B5'   # Fiscal mode closing
RE_REG_RESULT_REQ   = 'B6'   # The fiscalization (re-registration) result request
MF_STATUS_RESET     = 'B7'   # The MF status reset
SET_CSTMR_EMAIL     = 'B8'   # Set a customer's e-mail address
CORRECTION_RECEIPT  = 'B9'   # Create a correction receipt
PAYMENT_STATUS_REP  = 'BA'   # Create a payment status report
DOC_FA_ARCH_REQ     = 'BB'   # Request a document from the FA archive
FDO_DOC_SLIP_REQ    = 'BC'   # FDO document slip request
SET_FISCAL_DOC_ATTR = 'BD'   # Set a fiscal document attribute
PRINT_DOC_MF_ARCH   = 'BE'   # Print a document from the MF archive
SET_TAX_SYS_TYPE    = 'BF'   # Set the taxing system type

### RANDOM STUFF ###

FULL_CUT = 1
PARTIAL_CUT = 5

DEVICE_STATE_BITMAP = {
    0: 'Printer is not ready',
    1: 'No paper in printer',
    2: 'Printer cover is open',
    3: 'Error of printer cutter',
    7: 'No connection with printer',
}

PRINTER_RESPONSE_ERROR_CODES = {
    '01': 'Function is in executable at this status',
    '02': 'Invalid function number is indicated in command',
    '03': 'Invalid format or parameter of commands',
    '04': 'Overflow of communication port buffer',
    '05': 'Timeout at transfer information byte',
    '06': 'Invalid password is indicated in protocol',
    '07': 'Error of checksum in command',
    '08': 'Paper end',
    '09': 'Printer/display is not ready',
    '0A': 'Current shift is more than 24 hours. Setup of date/time is more than 24 hours.',
    '0B': 'Difference in time, internal clocks and indicated work beginning in command, more than 8 minutes',
    '0C': 'Input Date is earlier, than Date of the last fiscal operation',
    '0D': 'Invalid password for access to the FA',
    '0E': 'Negative result',
    '0F': 'The shift should be closed to execute command',
    '20': 'Fatal error. Reason of this error appeared you can specify in ”Status of fatal errors”',
    '21': 'No free space in fiscal memory',
    '42': 'Device response timeout',
}