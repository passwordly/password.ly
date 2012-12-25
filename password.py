import bcrypt
import hmac

bcrypt_alphabet = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';

def take(N, bignum):
  mod = bignum % N
  bignum = bignum / N
  return (mod, bignum)

def choice(letters, bignum):
  choice, bignum = take(len(letters), bignum)
  return (letters[choice], bignum)

def convertBase(result, alphabet):
  value = [alphabet.index(x) for x in result][::-1]
  return sum([value[k] * len(alphabet)**k for k in range(len(value))])

def createHash(password):
  salt = bcrypt.gensalt(11)
  return bcrypt.hashpw(password, salt)

def checkHash(password, hash):
  result = bcrypt.hashpw(password, hash)
  return (result == hash)

def generateSalt(password, site):
  result = hmac.new(password, site)

  bignum = 0
  for l in result.digest():
    bignum = (bignum * 256) + ord(l)

  salt = ''
  for k in range(22):
    letter, bignum = choice(bcrypt_alphabet, bignum)
    salt += letter

  return salt

def generatePassword(password, site):
  letters = 'abcdefghijklmnopqrstuvwxyz'
  u_letters = letters.upper()
  all_letters = letters + u_letters

  numbers = '0123456789'
  symbols = '!@#$%*-?+='
  length = 10

  salt = '$2a$11$' + generateSalt(password, site)

  bignum = convertBase(
    bcrypt.hashpw(password, salt)[len(salt):]
  , bcrypt_alphabet)


  # Create the final letters first
  password = [False] * (length - 1)

  # Pick atleast one of each group for the rest
  groups = [letters + u_letters, numbers, symbols]

  for group in groups:
    # Pick one of the remaining positions for this group
    remaining = [k for k in range(len(password)) if password[k] is False]
    position, bignum = choice(remaining, bignum)

    # Insert a choice from the group in the position
    password[position], bignum = choice(group, bignum)

  # Fill in any remaining letters
  for k in range(len(password)):
    if password[k] is False:
      password[k], bignum = choice(''.join(groups), bignum)

  # Finally pick a letter for the front
  front, bignum = choice(letters+u_letters, bignum)

  return front + ''.join(password)

