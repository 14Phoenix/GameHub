DROP TABLE IF EXISTS User_Participated;

DROP TABLE IF EXISTS Participate;

DROP TABLE IF EXISTS Team_Notification;

DROP TABLE IF EXISTS Forum_Notification;

DROP TABLE IF EXISTS Tour_Notification;

DROP TABLE IF EXISTS Tournament;

DROP TABLE IF EXISTS Forum_Num_Of_Players;

DROP TABLE IF EXISTS Notification;

DROP TABLE IF EXISTS Request_To_Join;

DROP TABLE IF EXISTS Message;

DROP TABLE IF EXISTS Team_Member;

DROP TABLE IF EXISTS Team;

DROP TABLE IF EXISTS Liked_Comment;

DROP TABLE IF EXISTS Comment;

DROP TABLE IF EXISTS Follow;

DROP TABLE IF EXISTS Moderates;

DROP TABLE IF EXISTS Admin;

DROP TABLE IF EXISTS Moderator;

DROP TABLE IF EXISTS Create_Tournament_User;

DROP TABLE IF EXISTS Liked_Post;

DROP TABLE IF EXISTS Post;

DROP TABLE IF EXISTS Forum;

-- DROP TABLE IF EXISTS Registered_User;


-- CREATE TABLE Registered_User
-- ( 
-- 	IDUser             int  auto_increment  NOT NULL ,
-- 	Email              varchar(254)  NOT NULL ,
-- 	Username           varchar(25)  NOT NULL ,
-- 	Password           varchar(50)  NOT NULL ,
-- 	Status             char(3)  NOT NULL DEFAULT 'ACT',
--     DateRegistered     datetime  NOT NULL ,
-- 	ProfilePicture     longblob  NULL ,
-- 	AboutSection       varchar(200)  NULL ,
--     PRIMARY KEY (IDUser),
--     UNIQUE KEY XAK1Registered_User (Email),
-- 	CONSTRAINT StatusCheckValues_897573113 CHECK  ( Status='ACT' OR Status='DEL' )
-- );

ALTER TABLE Registered_User
	MODIFY is_superuser tinyint(1) ,
    MODIFY first_name varchar(150) ,
    MODIFY last_name varchar(150) ,
    MODIFY is_staff tinyint(1) ,
    MODIFY is_active tinyint(1) DEFAULT 1 ,
    MODIFY date_joined datetime(6) ,
	ADD CONSTRAINT StatusCheckValues CHECK  ( Status='ACT' OR Status='DEL' ) ,
	CHANGE COLUMN `Status` `Status` char(3) NOT NULL DEFAULT 'ACT' ;


CREATE TABLE Forgot_Password (
    IDForgot int auto_increment NOT NULL,
    ResetKey varchar(37) NOT NULL,
    ExpirationDate datetime NOT NULL,
    IDUser int NOT NULL,
    PRIMARY KEY (IDForgot),
    UNIQUE KEY Unique_ResetKey (ResetKey),
    CONSTRAINT R_95 FOREIGN KEY (IDUser) REFERENCES Registered_User(IDUser) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE Create_Tournament_User
( 
	IDUser             int  NOT NULL ,
    PRIMARY KEY (IDUser) ,
    CONSTRAINT R_36 FOREIGN KEY (IDUser) REFERENCES Registered_User(IDUser) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE Moderator
( 
	IDMod              int  NOT NULL ,
    PRIMARY KEY (IDMod) ,
    CONSTRAINT R_34 FOREIGN KEY (IDMod) REFERENCES Create_Tournament_User(IDUser) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE Admin
( 
	IDAdmin            int  NOT NULL ,
    PRIMARY KEY (IDAdmin) ,
    CONSTRAINT R_35 FOREIGN KEY (IDAdmin) REFERENCES Create_Tournament_User(IDUser) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE Forum
( 
	IDForum            int  auto_increment  NOT NULL ,
	Name               varchar(50)  NOT NULL ,
	CoverImage         longblob  NOT NULL ,
	BannerImage        longblob  NOT NULL ,
	Description        varchar(1000)  NOT NULL ,
	Status             char(3)  NOT NULL DEFAULT 'ACT',
    DateCreated        datetime  NOT NULL ,
    PRIMARY KEY (IDForum),
	CONSTRAINT StatusCheckValues_541199655 CHECK  ( Status='ACT' OR Status='DEL' )
);


CREATE TABLE Forum_Num_Of_Players
( 
	IDForumNumOfPlayers int auto_increment NOT NULL ,
	IDForum            int  NOT NULL ,
	NumberOfPlayers    int  NOT NULL ,
    PRIMARY KEY (IDForumNumOfPlayers) ,
    UNIQUE Unique_IDForum_NumOfPlayers (IDForum, NumberOfPlayers) ,
    CONSTRAINT R_4 FOREIGN KEY (IDForum) REFERENCES Forum(IDForum) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE Follow
( 
	IDFollow		   int  auto_increment  NOT NULL ,
	IDUser             int  NOT NULL ,
	IDForum            int  NOT NULL ,
	DateFollowed       datetime  NOT NULL ,
    PRIMARY KEY (IDFollow) ,
    UNIQUE Unique_IDUser_IDForum (IDUser,IDForum) ,
    CONSTRAINT R_11 FOREIGN KEY (IDUser) REFERENCES Registered_User(IDUser) ON UPDATE CASCADE,
	CONSTRAINT R_12 FOREIGN KEY (IDForum) REFERENCES Forum(IDForum) ON UPDATE CASCADE
);


CREATE TABLE Moderates
( 
	IDModerates		   int  auto_increment  NOT NULL ,
	IDForum            int  NOT NULL ,
    IDMod              int  NOT NULL ,
	DatePromoted       datetime  NOT NULL ,
	IDAdmin            int  NULL ,
    PRIMARY KEY (IDModerates) ,
    UNIQUE Unique_IDForum_IDMod (IDForum,IDMod) ,
    CONSTRAINT R_10 FOREIGN KEY (IDForum) REFERENCES Forum(IDForum) ON UPDATE CASCADE,
	CONSTRAINT R_9 FOREIGN KEY (IDMod) REFERENCES Moderator(IDMod) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT R_13 FOREIGN KEY (IDAdmin) REFERENCES Admin(IDAdmin) ON DELETE SET NULL ON UPDATE CASCADE
);


CREATE TABLE Post
( 
	IDPost             int  auto_increment  NOT NULL ,
	IDForum            int  NOT NULL ,
	IDUser             int  NOT NULL ,
	Title              varchar(200)  NOT NULL ,
	Body               varchar(15000)  NULL ,
	Status             char(3)  NOT NULL DEFAULT 'ACT',
    DateCreated        datetime  NOT NULL ,
    PRIMARY KEY (IDPost) ,
    CONSTRAINT R_5 FOREIGN KEY (IDForum) REFERENCES Forum(IDForum) ON UPDATE CASCADE,
	CONSTRAINT R_6 FOREIGN KEY (IDUser) REFERENCES Registered_User(IDUser) ON UPDATE CASCADE,
    CONSTRAINT StatusCheckValues_1600196649 CHECK  ( Status='ACT' OR Status='DEL' )
);


CREATE TABLE Liked_Post
( 
	IDLike			   int  auto_increment  NOT NULL ,
	IDUser             int  NOT NULL ,
	IDPost             int  NOT NULL ,
	DateLiked          datetime  NOT NULL ,
    PRIMARY KEY (IDLike) ,
    UNIQUE Unique_IDUser_IDPost (IDUser,IDPost) ,
    CONSTRAINT R_7 FOREIGN KEY (IDUser) REFERENCES Registered_User(IDUser) ON UPDATE CASCADE,
	CONSTRAINT R_8 FOREIGN KEY (IDPost) REFERENCES Post(IDPost) ON UPDATE CASCADE
);


CREATE TABLE Comment
( 
	IDCom              int auto_increment NOT NULL ,
	IDUser             int  NOT NULL ,
	IDPost             int  NOT NULL ,
	Body               varchar(15000)  NOT NULL ,
	Status             char(3)  NOT NULL DEFAULT 'ACT',
    DateCreated        datetime  NOT NULL,
    PRIMARY KEY (IDCom),
    CONSTRAINT R_15 FOREIGN KEY (IDUser) REFERENCES Registered_User(IDUser) ON UPDATE CASCADE,
	CONSTRAINT R_16 FOREIGN KEY (IDPost) REFERENCES Post(IDPost) ON UPDATE CASCADE,
	CONSTRAINT StatusCheckValues_230435138 CHECK (Status='ACT' OR Status='DEL')
);


CREATE TABLE Liked_Comment
( 
	IDLike			   int  auto_increment  NOT NULL ,
	IDUser             int  NOT NULL ,
    IDCom              int  NOT NULL ,
	DateLiked          datetime  NOT NULL ,
    PRIMARY KEY (IDLike) ,
    UNIQUE Unique_IDUser_IDCom (IDUser,IDCom) ,
    CONSTRAINT R_17 FOREIGN KEY (IDUser) REFERENCES Registered_User(IDUser) ON UPDATE CASCADE,
	CONSTRAINT R_59 FOREIGN KEY (IDCom) REFERENCES Comment(IDCom) ON UPDATE CASCADE
);


CREATE TABLE Team
( 
	IDTeam             int  auto_increment  NOT NULL ,
	Name               varchar(20)  NOT NULL ,
	NumberOfPlayers    int  NOT NULL ,
	Status             char(3)  NOT NULL DEFAULT 'ACT',
    Description        varchar(200)  NOT NULL ,
	IDForum            int  NOT NULL ,
	DateCreated        datetime  NOT NULL ,
    PRIMARY KEY (IDTeam) ,
    CONSTRAINT R_21 FOREIGN KEY (IDForum) REFERENCES Forum(IDForum) ON UPDATE CASCADE,
	CONSTRAINT StatusCheckValues_1717377595 CHECK  ( Status='ACT' OR Status='DEL' )
);


CREATE TABLE Request_To_Join
( 
	IDReq              int  auto_increment  NOT NULL ,
	IDUser             int  NOT NULL ,
	IDTeam             int  NOT NULL ,
	RequestDate        datetime  NOT NULL ,
    PRIMARY KEY (IDReq) ,
    UNIQUE Unique_IDUser_IDTeam (IDUser,IDTeam) ,
    CONSTRAINT R_42 FOREIGN KEY (IDUser) REFERENCES Registered_User(IDUser) ON UPDATE CASCADE,
	CONSTRAINT R_43 FOREIGN KEY (IDTeam) REFERENCES Team(IDTeam) ON UPDATE CASCADE
);


CREATE TABLE Team_Member
( 
	IDMember           int  auto_increment  NOT NULL ,
	IDUser             int  NOT NULL ,
	IDForum            int  NOT NULL ,
	IDTeam             int  NOT NULL ,
	IsLeader           tinyint  NOT NULL DEFAULT 0,
	DateJoined         datetime  NOT NULL ,
	LastMsgReadDate    datetime  NOT NULL ,
    PRIMARY KEY (IDMember) ,
    UNIQUE Unique_IDUser_IDForum (IDUser,IDForum) ,
    CONSTRAINT R_24 FOREIGN KEY (IDUser) REFERENCES Registered_User(IDUser) ON UPDATE CASCADE,
	CONSTRAINT R_25 FOREIGN KEY (IDForum) REFERENCES Forum(IDForum) ON UPDATE CASCADE,
	CONSTRAINT R_26 FOREIGN KEY (IDTeam) REFERENCES Team(IDTeam) ON UPDATE CASCADE
);


CREATE TABLE Message
( 
	Body               varchar(2000)  NOT NULL ,
	IDMsg              int  auto_increment  NOT NULL ,
	IDTeam             int  NOT NULL ,
	IDUser             int  NOT NULL ,
	DateSent           datetime  NOT NULL ,
    PRIMARY KEY (IDMsg) ,
    CONSTRAINT R_29 FOREIGN KEY (IDUser) REFERENCES Registered_User(IDUser) ON UPDATE CASCADE,
	CONSTRAINT R_28 FOREIGN KEY (IDTeam) REFERENCES Team(IDTeam) ON UPDATE CASCADE
);


CREATE TABLE Tournament
( 
	IDTour             int  auto_increment  NOT NULL ,
	Name               varchar(30)  NOT NULL ,
	StartDate          datetime  NOT NULL ,
	NumberOfPlaces     int  NOT NULL ,
	Format             varchar(30)  NOT NULL ,
	IDForumNumOfPlayers	int  NOT NULL ,
	RewardValue        int  NOT NULL ,
	RewardCurrency     varchar(20)  NOT NULL ,
	DateCreated        datetime  NOT NULL ,
	Status             varchar(12)  NOT NULL DEFAULT  'NOT_STARTED' ,
    IDUser             int  NULL ,
    PRIMARY KEY (IDTour) ,
    CONSTRAINT R_30 FOREIGN KEY (IDForumNumOfPlayers) REFERENCES Forum_Num_Of_Players(IDForumNumOfPlayers) ON UPDATE CASCADE,
	CONSTRAINT R_37 FOREIGN KEY (IDUser) REFERENCES Create_Tournament_User(IDUser) ON DELETE SET NULL ON UPDATE CASCADE,
	CONSTRAINT TournamentStatus_628316031 CHECK  ( Status='NOT_STARTED' OR Status='IN_PROGRESS' OR Status='FINISHED' )
);


CREATE TABLE Participate
( 
	IDPar              int  auto_increment  NOT NULL ,
	IDTeam             int  NOT NULL ,
	IDTour             int  NOT NULL ,
	Position           int  NOT NULL ,
	Points             int  NOT NULL DEFAULT 0 ,
    PRIMARY KEY (IDPar) ,
    UNIQUE Unique_IDTeam_IDTour (IDTeam,IDTour) ,
    CONSTRAINT R_31 FOREIGN KEY (IDTeam) REFERENCES Team(IDTeam) ON UPDATE CASCADE,
	CONSTRAINT R_32 FOREIGN KEY (IDTour) REFERENCES Tournament(IDTour) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE User_Participated
( 
	IDUserPar          int  auto_increment  NOT NULL ,
	IDPar              int  NOT NULL ,
	IDUser             int  NOT NULL ,
    PRIMARY KEY (IDUserPar) ,
    UNIQUE (IDPar,IDUser) ,
    CONSTRAINT R_56 FOREIGN KEY (IDPar) REFERENCES Participate(IDPar) ON UPDATE CASCADE,
	CONSTRAINT R_58 FOREIGN KEY (IDUser) REFERENCES Registered_User(IDUser) ON UPDATE CASCADE
);


CREATE TABLE Notification
( 
	IDUser             int  NOT NULL ,
	IDNot              int  auto_increment  NOT NULL ,
	DateSent           datetime  NOT NULL ,
    PRIMARY KEY (IDNot) ,
    CONSTRAINT R_39 FOREIGN KEY (IDUser) REFERENCES Registered_User(IDUser) ON DELETE RESTRICT ON UPDATE CASCADE
);


CREATE TABLE Forum_Notification
( 
	IDNot              int  NOT NULL ,
	IDPost             int  NULL ,
	IDForum            int  NOT NULL ,
	Type               varchar(12)  NOT NULL ,
    PRIMARY KEY (IDNot) ,
    CONSTRAINT R_48 FOREIGN KEY (IDNot) REFERENCES Notification(IDNot) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT R_50 FOREIGN KEY (IDPost) REFERENCES Post(IDPost) ON UPDATE CASCADE,
	CONSTRAINT R_51 FOREIGN KEY (IDForum) REFERENCES Forum(IDForum) ON UPDATE CASCADE,
	CONSTRAINT PostNotificationT_521733190 CHECK  ( Type='POST_DEL' OR Type='POST_NEW' OR Type='MOD_DELETED' OR Type='MOD_ADDED' )
);


CREATE TABLE Team_Notification
( 
	IDNot              int  NOT NULL ,
	IDTeam             int  NOT NULL ,
	IDUser             int  NULL ,
	Type               varchar(12)  NOT NULL ,
    PRIMARY KEY (IDNot) ,
    CONSTRAINT R_52 FOREIGN KEY (IDNot) REFERENCES Notification(IDNot) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT R_53 FOREIGN KEY (IDTeam) REFERENCES Team(IDTeam) ON UPDATE CASCADE,
	CONSTRAINT R_54 FOREIGN KEY (IDUser) REFERENCES Registered_User(IDUser) ON UPDATE CASCADE,
	CONSTRAINT TeamNotificationTypeValues_1428983534 CHECK  ( Type='TEAM_INVITE' OR Type='TEAM_LEAVE' OR Type='TEAM_JOINED' OR Type='NEW_MSG' )
);


CREATE TABLE Tour_Notification
( 
	IDNot              int  NOT NULL ,
	IDTour             int  NULL ,
	Type               varchar(13)  NOT NULL ,
    PRIMARY KEY (IDNot) ,
    CONSTRAINT R_46 FOREIGN KEY (IDNot) REFERENCES Notification(IDNot) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT R_47 FOREIGN KEY (IDTour) REFERENCES Tournament(IDTour) ON DELETE SET NULL ON UPDATE CASCADE,
	CONSTRAINT TourNotificationTypeValues_1009222864 CHECK  ( Type='TOUR_JOINED' OR Type='TOUR_STARTED' OR Type='TOUR_KICKED' )
);
