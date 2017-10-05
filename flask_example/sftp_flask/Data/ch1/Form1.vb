Public Class Form1

    Dim num As String = ""
    Private Sub Button1_Click(sender As Object, e As EventArgs) Handles Button1.Click
        num = (Convert.ToInt64(TextBox1.Text) + Convert.ToInt64(TextBox2.Text)).ToString()
    End Sub

    Private Sub Button2_Click(sender As Object, e As EventArgs) Handles Button2.Click
        num = (Convert.ToInt64(TextBox1.Text) - Convert.ToInt64(TextBox2.Text)).ToString()
    End Sub

    Private Sub Button3_Click(sender As Object, e As EventArgs) Handles Button3.Click
        num = (Convert.ToInt64(TextBox1.Text) * Convert.ToInt64(TextBox2.Text)).ToString()
    End Sub

    Private Sub Button4_Click(sender As Object, e As EventArgs) Handles Button4.Click
        If Convert.ToInt64(TextBox2.Text) = 0 Then
            num = "Invalid Args."
        Else
            num = (Convert.ToInt64(TextBox1.Text) / Convert.ToInt64(TextBox2.Text)).ToString()
        End If
    End Sub

    Private Sub Button5_Click(sender As Object, e As EventArgs) Handles Button5.Click
        TextBox3.Text = num
    End Sub

    Private Sub Button6_Click(sender As Object, e As EventArgs) Handles Button6.Click
        TextBox1.Text = 0
        TextBox2.Text = 0
        TextBox3.Text = 0
    End Sub
End Class
