from ytune.player import Player


def test_get_stream_url_mocked(mocker):
    mocker.patch("ytune.player.mpv")

    mock_ydl = mocker.patch("yt_dlp.YoutubeDL")
    mock_instance = mock_ydl.return_value.__enter__.return_value
    mock_instance.extract_info.return_value = {"url": "http://stream.url"}

    player = Player()
    url = player.get_stream_url("vid123")

    assert url == "http://stream.url"
    mock_instance.extract_info.assert_called_with(
        "https://www.youtube.com/watch?v=vid123", download=False
    )

def test_player_play_calls_mpv(mocker):
    # Mock mpv in the player module
    mock_mpv_module = mocker.patch("ytune.player.mpv")
    mock_mpv_instance = mock_mpv_module.MPV.return_value
    
    # Mock yt-dlp to return a fixed URL
    mock_ydl = mocker.patch("yt_dlp.YoutubeDL")
    mock_ydl.return_value.__enter__.return_value.extract_info.return_value = {"url": "http://test.url"}
    
    player = Player()
    player.play("vid123")
    
    # Verify mpv play was called with the URL from yt-dlp
    mock_mpv_instance.play.assert_called_with("http://test.url")
