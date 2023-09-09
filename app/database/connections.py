from .db import FileManager, DataManager, UserManager, TimedDataManager

UserDB = UserManager("Auth", "Users")
PendingUserDB = TimedDataManager("Auth", "Pending")
AuthCodesDB = TimedDataManager("Auth", "Codes")
invalidAccessTokensDB = TimedDataManager("Auth", "LoggedOutTokens")

imagesDB = FileManager('Images')
albemsDB = DataManager("Instances", "Albem")