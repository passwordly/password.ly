import bcrypt
import hmac

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

def generatePassword(password, site):
  bcrypt_alphabet = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
  letters = 'abcdefghijklmnopqrstuvwxyz'
  u_letters = letters.upper()
  all_letters = letters + u_letters

  numbers = '0123456789'
  symbols = '!@#$%*-?+='
  length = 10


  # Make sure the site is made entirely of bcrypt allowable letters
  if any([l not in bcrypt_alphabet for l in site]):
    raise Exception('site can only contain: %s' % bcrypt_alphabet)

  salt_maker = hmac.new(((site + password)*22)[:22])
  salt = '$2a$11$' + salt_maker.hexdigest()

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

print generatePassword('u$fC8*Al', 'gmail')    # s+20hU05ZV
print generatePassword('u$fC8*Al', 'facebook') # u=@Szg5$3y
print generatePassword('u$fC8*Al', 'itunes')   # I?33G7zy-T
print generatePassword('G(@oR2xL', 'itunes')   # mc0*2aJUGJ
