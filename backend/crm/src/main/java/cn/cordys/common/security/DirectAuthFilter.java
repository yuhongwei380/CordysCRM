package cn.cordys.common.security;

import cn.cordys.security.SessionConstants;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.lang3.StringUtils;
import org.apache.shiro.SecurityUtils;
import org.apache.shiro.authc.UsernamePasswordToken;
import org.apache.shiro.web.filter.authc.AnonymousFilter;

import java.nio.charset.StandardCharsets;

/**
 * Allow direct API access via Basic or Bearer auth without cookies/CSRF.
 * - Basic: Authorization: Basic base64(user:pass)
 * - Bearer: Authorization: Bearer <token>, mapped to configured user (default admin).
 * Basic relies on password verification; Bearer trusts a static token.
 */
public class DirectAuthFilter extends AnonymousFilter {

    private final boolean basicEnabled;
    private final String bearerToken;
    private final String bearerUser;

    public DirectAuthFilter(boolean basicEnabled, String bearerToken, String bearerUser) {
        this.basicEnabled = basicEnabled;
        this.bearerToken = bearerToken;
        this.bearerUser = bearerUser;
    }

    @Override
    protected boolean onPreHandle(ServletRequest request, ServletResponse response, Object mappedValue) {
        HttpServletRequest httpReq = (HttpServletRequest) request;
        HttpServletResponse httpResp = (HttpServletResponse) response;

        String authorization = httpReq.getHeader("Authorization");
        if (StringUtils.isBlank(authorization)) {
            return true;
        }

        if (authorization.startsWith("Basic ") && basicEnabled) {
            return handleBasic(authorization.substring(6), httpResp);
        }

        if (authorization.startsWith("Bearer ") && StringUtils.isNotBlank(bearerToken)) {
            return handleBearer(authorization.substring(7), httpResp);
        }

        return true;
    }

    private boolean handleBasic(String base64, HttpServletResponse resp) {
        try {
            String decoded = new String(Base64.decodeBase64(base64), StandardCharsets.UTF_8);
            int idx = decoded.indexOf(':');
            if (idx <= 0) {
                return true;
            }
            String user = decoded.substring(0, idx);
            String pass = decoded.substring(idx + 1);
            if (StringUtils.isAnyBlank(user, pass)) {
                return true;
            }

            UsernamePasswordToken token = new UsernamePasswordToken(user, pass);
            SecurityUtils.getSubject().getSession().setAttribute("authenticate", "LOCAL");
            SecurityUtils.getSubject().login(token);
            return true;
        } catch (Exception e) {
            setUnauthorized(resp);
            return false;
        }
    }

    private boolean handleBearer(String token, HttpServletResponse resp) {
        if (!StringUtils.equals(token, bearerToken)) {
            setUnauthorized(resp);
            return false;
        }
        try {
            // Password is irrelevant; LocalRealm login path will fetch user and skip password when authenticate!=LOCAL.
            UsernamePasswordToken upToken = new UsernamePasswordToken(bearerUser, SessionConstants.AUTHENTICATION_INVALID);
            SecurityUtils.getSubject().getSession().setAttribute("authenticate", "BYPASS");
            SecurityUtils.getSubject().login(upToken);
            return true;
        } catch (Exception e) {
            setUnauthorized(resp);
            return false;
        }
    }

    private void setUnauthorized(HttpServletResponse resp) {
        resp.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
    }
}
