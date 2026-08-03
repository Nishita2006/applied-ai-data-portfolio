package com.nishita.jobportal.service;
import com.nishita.jobportal.entity.UserAccount;
import com.nishita.jobportal.exception.NotFoundException;
import com.nishita.jobportal.repository.UserRepository;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;
@Service public class CurrentUserService{
 private final UserRepository users; public CurrentUserService(UserRepository users){this.users=users;}
 public UserAccount require(Authentication auth){return users.findByEmailIgnoreCase(auth.getName()).orElseThrow(()->new NotFoundException("User not found"));}
}
