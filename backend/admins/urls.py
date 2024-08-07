from django.urls import path
 
from .views import *

urlpatterns = [
    path('login/',AdminLogin.as_view(), name='admin_login'),
    path('forums/', ForumListCreate.as_view(), name='forum-list-create'),
    path('forums/<int:pk>/update/', ForumUpdateView.as_view(), name='forum-update'),
    path('forums/<int:pk>/delete/', ForumDeleteView.as_view(), name='forum-delete'),
    path('speakers/', SpeakerListCreate.as_view(), name='speaker-list-create'),
    path('speakers/<int:pk>/', SpeakerRetrieve.as_view(), name='speaker-detail'),
    path('speakers/<int:pk>/update/', SpeakerUpdateView.as_view(), name='speaker-update'),
    path('speakers/<int:pk>/delete/', SpeakerDeleteView.as_view(), name='speaker-delete'), 
    path('eventcreate/', EventListCreate.as_view() , name='event_create'),
    path('events/', EventListView.as_view(), name='events-list'),  
    path('allevents/', EventListAllView.as_view(), name='allevents-list'),   
    path('events/<int:event_id>/update/', EventUpdateAPIView.as_view(), name='event-update'),
    path('events/<int:pk>/list/', EventListSingleView.as_view(), name='event-detail'),
    path('eventslist/', EventListView.as_view(), name='event-list'),
    path('events/<slug:slug>/', SingleEventDetailView.as_view(), name='single-events-detail'),
    path('enroll/<slug:slug>/single-events/', SingleDetailView.as_view(), name='single-events-enroll'),
     path('events/<slug:slug>/speakers/', EventSpeakersView.as_view(), name='event-speakers'),
    path('eventslistb/', EventListbannerView.as_view(), name='event-list'),
    path('members/', MemberListCreate.as_view(), name='member-list-create'),
    path('members/<int:pk>/update/', MemberUpdateView.as_view(), name='member-update'),
    path('members/<int:pk>/delete/', MemberDeleteView.as_view(), name='member-delete'),
    path('forummembers/', ForumMemberCreateView.as_view(), name='member-create'),
    path('forummembers/<int:forum_id>/', ForumMemberListView.as_view(), name='forum_members_list'),
    path('forummembers/<int:forum_id>/update/', ForumMemberView.as_view(), name='update_forum_member'),
    path('blogs/', CreateBlog.as_view(), name='blog_admin'),
    path('blogslist/', BlogListView.as_view(), name='blog-list'),
    path('blogslistall/', BlogListViewall.as_view(), name='blog-list'),
    path('blogs/<int:pk>/delete/', BlogDeleteView.as_view(), name='blogs-delete'),
    path('blogs/<int:pk>/update/', BlogUpdateView.as_view(), name='forum-update'),
    path('certificates/',certificatesCreate.as_view(), name='certificate-list-create'),
    path('certificates/<int:pk>/delete', CertificatesDeleteView.as_view(), name='certificates-delete'),
    path('certificateslist/', CertificatesList.as_view(), name='certificates-list'),
    path('certificates/<int:pk>/', CertificatesDetail.as_view(), name='certificate-detail'),
    path('banner/', BannerListCreate.as_view(), name='banner-list-create'),
    path('banner/<int:pk>/update/', BannerUpdateView.as_view(), name='banner-update'),
    path('banner/<int:pk>/delete/', BannerDeleteView.as_view(), name='banner-delete'),
    path('news/', NewsListCreate.as_view(), name='news-list-create'),
    path('news/<int:pk>/update/', NewsUpdateView.as_view(), name='news-update'),
    path('news/<int:pk>/delete/', NewsDeleteView.as_view(), name='news-delete'),
    path('forums/<int:forum_id>/members/', ForumMemberList.as_view(), name='forum-members'), 
    path('forums_get/',  ForumListView.as_view(), name='forum-get'),
    path('forums_get_member/',  ForumLisMembertView.as_view(), name='forum-get_member'),
    path('members_exclude/<int:forum_id>/', ForumExcludeView.as_view(), name='forum_exclude'),
    path('boards/', BoardListCreate.as_view(), name='boards-list-create'),
    path('boards/<int:pk>/update/', BoardUpdateView.as_view(), name='board-update'),
    path('boards/<int:pk>/delete/', BoardDeleteView.as_view(), name='board-delete'),
    path('boards_get/',  BoardListView.as_view(), name='board-get'),
    path('boards_get_member/',  BoardLisMembertView.as_view(), name='board-get_member'),
    path('members_exclude/<int:board_id>/', BoardExcludeView.as_view(), name='board_exclude'),
    path('boardmembers/', BoardMemberCreateView.as_view(), name='member-create'),
    path('boardmembers/<int:board_id>/', BoardMemberListView.as_view(), name='board_members_list'),
    path('boardmembers/<int:board_id>/update/', BoardMemberView.as_view(), name='board_board_member'),
    path('allboardmembers/', AllBoardMembersView.as_view(), name='all_board_members'),
    path('members/<slug:slug>/detail/', MemberDetailViewBySlug.as_view(), name='member_detail_by_slug'),
    path('forums/<slug:slug>/', EventForumListView.as_view(), name='forum-events'),
    path('blogsforum/<slug:slug>/', BlogForumListView.as_view(), name='blog-list'),
    path('forumsyear/<slug:slug>/', EventForumYearView.as_view(), name='forum-events'),
    path('blogsyear/<slug:slug>/', BlogForumYearView.as_view(), name='blog-list'),
    path('forum/<slug:slug>/events/', EventTodayView.as_view(), name='event-forum-list'),
    path('forumweek/<slug:slug>/events/', EventThisWeekView.as_view(), name='eventweek-forum-list'),
    path('forummonth/<slug:slug>/events/', EventThisMonthView.as_view(), name='eventmonth-forum-list'),
    path('forumyear/<slug:slug>/events/', EventThisYearView.as_view(), name='eventyear-forum-list'),
    path('blogs-detail/<slug:slug>/', BlogDetailView.as_view(), name='blog-detail'),
    path('eventstoday/', EventUserToday.as_view(), name='event-today-list'),
    path('eventsweek/', EventUserThisWeek.as_view(), name='event-week-list'),
    path('eventsmonth/', EventThisMonthUser.as_view(), name='event-month-list'),
    path('eventsyear/', EventThisYearUser.as_view(), name='event-year-list'),
    path('add-gallery/', AddGalleryView.as_view(), name='add-gallery'),
    path('gallery/', GetGalleryView.as_view(), name='get_gallery_images'),
    path('update-gallery/<int:pk>/', UpdateGalleryView.as_view(), name='update_gallery'),
    path('delete-gallery/<int:gallery_id>/', DeleteGalleryView.as_view(), name='delete_gallery'),
    path('events/<int:event_id>/delete/', EventDeleteAPIView.as_view(), name='event-delete'),
    path('upload/', UploadAttachmentView.as_view(), name='upload_attachment'),
    path('single-events-all/', SingleEventListAllView.as_view(), name='single-event-list'),
    path('attachments/<int:pk>/update/', UpdateAttachmentView.as_view(), name='update-attachment'),
    path('attachments/', AttachmentsBySingleEventView.as_view(), name='retrieve-attachment'),
    path('attachments-all/', ListAttachmentsView.as_view(), name='list-attachments'),
    path('attachments/<int:pk>/delete/', AttachmentDeleteAPIView.as_view(), name='attachment-delete'),
    path('user-file-interaction/', AssociateFileWithUserView.as_view(), name='user-file-interaction'),
    path('user-attachments/', UserAttachmentsView.as_view(), name='user-attachments'),
]     
 